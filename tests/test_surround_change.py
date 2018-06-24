import os
import unittest

import sublime

from sublime import Region as R

from User.six.tests import ViewTest

from Six.lib.command_state import CommandState
from Six.lib.constants import Mode
from Six.lib.errors import AbortCommandError
from Six.lib.yank_registers import EditOperation

from User.six.surround import find_in_line
from User.six.surround import BRACKETS


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


class Test__six_surround_change_Success(ViewTest):

    def testCanReplace(self):
        self.view.run_command("append", { "characters": "aaa 'bbb' ccc" })
        self.view.sel().clear()
        self.view.sel().add(R(5))

        old = "'"

        for new, brackets in BRACKETS.items():
            # with self.subTest(bracket=new): # Not supported in Python 3.3
            old_a, old_b = BRACKETS[old]
            new_a, new_b = brackets

            self.assertEquals(self.view.substr(4), old_a)
            self.assertEquals(self.view.substr(8), old_b)

            self.view.run_command("_six_surround_change", { "old": old, "new": new })

            self.assertEquals(self.view.substr(4), new_a)
            self.assertEquals(self.view.substr(8), new_b)

            old = new

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
