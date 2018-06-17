"""Surround plugin for Sublime Six"""

import logging

import sublime
import sublime_plugin

from sublime import Region as R

IS_SIX_ENABLED = False

try:
    from Six.lib.errors import AbortCommandError
except ImportError:
    pass
else:
    IS_SIX_ENABLED = True

# Hook ourselves up to the Six logger. Anyhing prefixed with "Six." is fine,
# but let's establish a standard (there's a "plugin" folder in Six, hence
# "user.plugin" here.)
_logger = logging.getLogger("Six.user.plugin.surround")

# Limit stuff that gets exported to global scope.
__all__ = (
    # TextCommand needs to be available to Sublime Text.
    "_six_surround_change",
    # We need this for initialization from Packages/User/sixrc.py.
    "surround",
)


BRACKETS = {
    "'": ("'", "'"),
    '"': ('"', '"'),
    "(": ("(", ")"),
    ")": ("(", ")"),
    "[": ("[", "]"),
    "]": ("[", "]"),
    r"{": ("{", "}"),
    r"}": ("{", "}"),
}

# Initialization function. We need this to control initialization from other
# modules and account for the case where Six isn't available.
def surround(register=True):
    """Define the Six command processor class for the Surround change plugin.

    :param register:
        If `True`, it registers the command in addition to defining it. This
        is the standard case.

    Returns the defined class. User code will mostly ignore the return value,
    but it's interesting for testing.
    """
    from Six._init_ import editor
    from Six.lib.constants import Mode
    from Six.lib.errors import AbortCommandError
    from Six.lib.operators_internal import (
        OperatorWithoutMotion, )
    from Six.lib.yank_registers import EditOperation

    # Our command doesn't need a motion; it's implicit.
    class SurroundChangeSixPlugin(OperatorWithoutMotion):
        """Implement Six command processing for the Surround change command.
        """

        def __init__(self, *args, **kwargs):
            # Give our command a name to satisfy the base class.
            super().__init__("zs", *args, **kwargs)
            # We want to replace this delimiter...
            self.old = None
            # ... with this other delimiter.
            self.new = None

        # We shouldn't need to implement this as an operator. But because we are
        # technically inside an OperatorOrMotion (z), we must, at least for now.
        def set_parent(self, parent):
            pass

        # This property is used in the context of yanking. Generally speaking,
        # plugins should return EditOperation.Other.
        @property
        def kind(self):
            return EditOperation.Other

        def process(self, mode, state):
            # If you run this, you will see how the keys build up as you press them.
            _logger.info("processing keys... %s", state.keys)
            # Let OperatorWithoutMotion do its part. Since most commands of this
            # kind do the same thing, the behavior is encapsulated in the base
            # class. But we are a bit of a snowflake, so we need to adjust a few
            # things below.
            super().process(mode, state)

            # We need to collect two keys, one for the old delimiter; the other
            # for the new one.
            for i in range(2):
                # "state", aka "command state", gives us useful information about
                # the in-flight command. And mutating its fields, we can communicate
                # back with the Editor in charge of managing us should we need to.
                if state.is_at_eof:
                    # No more keys from user available -- request more.
                    state.more_input = True
                    return

                # The key index is incremented for us as keys are consumed while
                # the command is processed upstream. At this point, zs have been
                # consumed. Let's satisfy our requirements now if we can.
                key = state.next()

                # TODO: support more delimiters.
                if key not in BRACKETS:
                    # Let the Editor know that something went wrong. Maybe this
                    # isn't the best error to raise here, but it'll do for now.
                    raise AbortCommandError

                if i == 0:
                    # First available key.
                    self.old = key
                else:
                    # Second available key.
                    self.new = key

            # Done! The command is ready to be executed next.
            state.more_input = False

        def execute(self, mode, times=1, register='"'):
            if self.old == self.new:
                # User is tired. Stop. We could complain too; not sure what the
                # actual Vim Surround plugin does.
                _logger.info("no change needed; stop here")
            else:
                # This is a bit ugly and Six should help us hide these details,
                # but that isn't ready yet.
                view = sublime.active_window().active_view()
                # The processing Six needs to do before we can actually change
                # the Sublime Text state is done. Delegate to an ST command. After
                # we've done our thing in ST, Six will run the Six command's
                # lifecycle to its end (mainly calling our .reset() below and
                # cleaning up the global Six state).
                view.run_command("_six_surround_change", {
                    "old": self.old,
                    "new": self.new
                    })

        def reset(self):
            # The Six Editor will call us to give us a chance to clean up after
            # we have been executed.
            _logger.info("resetting...")
            super().reset()
            self.old = None
            self.new = None

    if register:
        # TODO: use cs for keys instead when c can act as a namespace.
        # Register this command for the given mode and assign it the given key sequence.
        editor.register(mode=Mode.Normal, keys="zs")(SurroundChangeSixPlugin)

    return SurroundChangeSixPlugin


# We don't load the ST commands if Six isn't available.
if IS_SIX_ENABLED:

    class _six_surround_change(sublime_plugin.TextCommand):
        """Replaces delimiters.

        For example, zs'" replaces (') with (") if we are currently inside a string
        delimited by (').
        """

        def run(self, edit, old, new):
            # The drudgery above is necessary only to reach this point, where we
            # know exactly what Sublime Text needs to do.
            old_a, old_b = BRACKETS[old]
            new_a, new_b = BRACKETS[new]

            a = find_in_line(self.view, old_a, forward=False)
            if a < 0:
                # TODO: Signal the state that it should abort.
                # Caller can't catch this exception from the command; just stop.
                # raise AbortCommandError
                return

            b = find_in_line(self.view, old_b)
            if b < 0:
                # TODO: Signal the state that it should abort.
                # Caller can't catch this exception from the command; just stop.
                # raise AbortCommandError
                return

            self.view.replace(edit, R(a, a + 1), new_a)
            self.view.replace(edit, R(b, b + 1), new_b)

    def find_in_line(view, character, forward=True):
        """Find a character in the current line.
        :param view:
            The view where we are performing the search.
        :param character:
            The sought character.
        :param forward:
            Whether to search forward or backwards.

        Returns 0 or a positive integer if the character was found. The number indicates
        the character position in the view. Returns a negative number if the character
        wasn't found.
        """
        pt = view.sel()[0].b
        limit = view.line(pt).end() if forward else view.line(pt).begin()
        is_within_limits = (lambda x: x < limit) if forward else (lambda x: x >= limit)
        increment = 1 if forward else -1

        while is_within_limits(pt):
            if view.substr(pt) == character:
                break
            pt += increment
        else:
            return -1

        return pt
