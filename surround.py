# TODO: Add tests and CI integration.
import logging

import sublime
import sublime_plugin


# Hook ourselves up to the Six logger. Anyhing prefixed with 'Six.' is fine,
# but let's establish a standard (there's a 'plugin' folder in Six, hence
# 'user.plugin' here.')
_logger = logging.getLogger('Six.user.plugin.surround')

# Limit stuff that gets exported to global scope.
__all__ = (
    # TextCommand needs to be available to Sublime Text.
    '_six_surround_change',
    # We need this for initialization from Packages\User\sixrc.py.
    'surround',
    )


IS_SIX_ENABLED = False


# Initialization function. We need this to control initialization from other modules and account
# for the case where Six isn't available.
def surround():
    global IS_SIX_ENABLED
    IS_SIX_ENABLED = True

    from Six._init_ import editor
    from Six.lib.constants import Mode
    from Six.lib.errors import AbortCommandError
    from Six.lib.operators_internal import OperatorWithoutMotion

    # TODO: use cs for keys instead when c can act as a namespace.
    # Register this command for the given mode and assign it the given key sequence.
    @editor.register(mode=Mode.Normal, keys="zs")
    # Our command doesn't need a motion; it's implicit.
    class SurroundChangeSixPlugin(OperatorWithoutMotion):

        def __init__(self, *args, **kwargs):
            # Give our command a name to satisfy the base class.
            super().__init__('zs', *args, **kwargs)
            # We want to replace this delimiter...
            self.old = None
            # ... with this other delimiter.
            self.new = None

        # We shouldn't need to implement this as an operator. But because we are
        # technically inside an OperatorOrMotion (z), we must, at least for now.
        def set_parent(self, parent):
            pass

        def process(self, mode, state):
            # If you run this, you will see how the keys build up as you press them.
            _logger.info("processing keys... %s" % state.keys)
            # Let OperatorWithoutMotion do its part. Since most commands of this
            # kind do the same thing, the behavior is encapsulated in the base
            # class. But we are a bit of a snowflake, so we need to adjust a few
            # things below.
            super().process(mode, state)

            # We need to collect two keys, one for the old delimiter; the other
            # for the new one.
            for i in range(2):
                # 'state', aka 'command state', gives us useful information about
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
                if key not in ('"', "'"):
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

        def execute(self, mode, times, register):
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
                view.run_command('_six_surround_change', {
                    'from_': self.old,
                    'to': self.new
                    })

        def reset(self):
            # The Six Editor will call us to give us a chance to clean up after
            # we have been executed.
            _logger.info("resetting...")
            super().reset()
            self.old = None
            self.new = None


class _six_surround_change(sublime_plugin.TextCommand):
    """Replaces delimiters.

    For example, zs'" replaces (') with (") if we are currently inside a string
    delimited by (').
    """
    def is_enabled(self, *args):
        return IS_SIX_ENABLED

    def run(self, edit, from_, to):
        # The drudgery above is necessary only to reach this point, where we
        # know exactly what Sublime Text needs to do. Now we have to implement it.
        _logger.info("doing the heavy lifting here... replacing {} with {}".format(from_, to))
