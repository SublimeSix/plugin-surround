import os
import unittest

import sublime

from sublime import Region as R

from Six.lib.command_state import CommandState
from Six.lib.constants import Mode
from Six.lib.errors import AbortCommandError
from Six.lib.yank_registers import EditOperation

from User.six.surround import BRACKETS


class Test_SupportedBrackets(unittest.TestCase):

    def testSupportsQuotationMarks(self):
        self.assertEquals(BRACKETS["'"], ("'", "'"))
        self.assertEquals(BRACKETS['"'], ('"', '"'))

    def testSupportsBrackets(self):
        self.assertEquals(BRACKETS["("], ("(", ")"))
        self.assertEquals(BRACKETS[")"], ("(", ")"))

    def testSupportsSquaredBrackets(self):
        self.assertEquals(BRACKETS["["], ("[", "]"))
        self.assertEquals(BRACKETS["]"], ("[", "]"))

    def testSupportsCurlyBracket(self):
        self.assertEquals(BRACKETS[r"{"], ("{", "}"))
        self.assertEquals(BRACKETS["}"], ("{", "}"))
