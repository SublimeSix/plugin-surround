import os
import unittest

import sublime

from sublime import Region as R

from Six.lib.command_state import CommandState
from Six.lib.constants import Mode
from Six.lib.errors import AbortCommandError
from Six.lib.yank_registers import EditOperation

from User.six.surround import find_in_line


class ViewTest(unittest.TestCase):

    def setUp(self):
        self.window = sublime.active_window()
        self.view = self.window.new_file()
        self.view.set_scratch(True)

    def tearDown(self):
        self.window.run_command('close')


class Test_find_in_line(ViewTest):

    def testReturnsNegativeNumberIfNotFound(self):
        self.view.run_command("append", { "characters": "aaa\nbbb\nccc" })
        self.view.sel().clear()
        self.view.sel().add(R(5))

        rv = find_in_line(self.view, "x")

        self.assertTrue(rv < 0)

    def testReturnsPointIfFound(self):
        self.view.run_command("append", { "characters": "aaa\nbbx\nccc" })
        self.view.sel().clear()
        self.view.sel().add(R(5))

        rv = find_in_line(self.view, "x")

        self.assertEquals(rv, 6)

    def testReturnsNegativeNumberIfNotFoundReversed(self):
        self.view.run_command("append", { "characters": "aaa\nbbb\nccc" })
        self.view.sel().clear()
        self.view.sel().add(R(5))

        rv = find_in_line(self.view, "x", forward=False)

        self.assertTrue(rv < 0)

    def testReturnsPointIfFoundReversed(self):
        self.view.run_command("append", { "characters": "aaa\nxbb\nccc" })
        self.view.sel().clear()
        self.view.sel().add(R(6))

        rv = find_in_line(self.view, "x", forward=False)

        self.assertEquals(rv, 4)


@unittest.skip("view.run_command does not reaise error in test")
class Test__six_surround_change_Errors(ViewTest):

    def testFailIfCannotFindLeftBracket(self):
        self.view.sel().clear()
        self.view.sel().add(R(0))

        old = "'"
        new = None
        def fail():
            self.view.run_command("_six_surround_change", { "old": old, "new": new })

        self.assertRaises(ValueError, fail)


    def testFailIfCannotFindRightBracket(self):
        self.view.run_command("append", { "characters": "aaa 'bbb ccc" })
        self.view.sel().clear()
        self.view.sel().add(R(5))

        old = "'"
        new = '"'
        def fail():
            self.view.run_command("_six_surround_change", { "old": old, "new": new })

        self.assertRaises(ValueError, fail)


@unittest.skipIf(sublime.platform() == "linux" and os.environ["TRAVIS"], "always fails in Travis-CI for Linux")
class Test__six_surround_change_Success(ViewTest):

    def testCanReplace(self):
        self.view.run_command("append", { "characters": "aaa 'bbb' ccc" })
        self.view.sel().clear()
        self.view.sel().add(R(5))

        self.assertEquals(self.view.substr(4), "'")
        self.assertEquals(self.view.substr(8), "'")

        self.view.run_command("_six_surround_change", { "old": "'", "new": '"' })

        self.assertEquals(self.view.substr(4), '"')
        self.assertEquals(self.view.substr(8), '"')

    def testCanUndoInOneStep(self):
        self.view.run_command("append", { "characters": "aaa 'bbb' ccc" })
        self.view.sel().clear()
        self.view.sel().add(R(5))

        self.assertEquals(self.view.substr(4), "'")
        self.assertEquals(self.view.substr(8), "'")

        self.view.run_command("_six_surround_change", { "old": "'", "new": '"' })

        self.assertEquals(self.view.substr(4), '"')
        self.assertEquals(self.view.substr(8), '"')

        self.view.run_command("undo")

        self.assertEquals(self.view.substr(4), "'")
        self.assertEquals(self.view.substr(8), "'")
