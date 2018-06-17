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
