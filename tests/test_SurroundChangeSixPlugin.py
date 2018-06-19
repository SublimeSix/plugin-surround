import unittest
from unittest import mock

import sublime

from Six.lib.command_state import CommandState
from Six.lib.constants import Mode
from Six.lib.errors import AbortCommandError
from Six.lib.yank_registers import EditOperation
from User.six.surround import surround


class ViewTest(unittest.TestCase):

    def setUp(self):
        self.window = sublime.active_window()
        self.view = self.window.new_file()
        self.view.set_scratch(True)

    def tearDown(self):
        self.window.run_command('close')


class TestSurroundChangeSixPluginBase(unittest.TestCase):

    def setUp(self):
        cls = surround(register=False)
        self.command = cls()
        self.state = CommandState()


class Test__init__(TestSurroundChangeSixPluginBase):

    def test___init__(self):
        self.assertEquals("CSurround", self.command.name)
        self.assertEquals(EditOperation.Other, self.command.kind)
        self.assertIsNone(self.command.old)
        self.assertIsNone(self.command.new)


class Test_process(TestSurroundChangeSixPluginBase):

    def test_RequestsMoreInputIfNoInputAvailable(self):
        self.assertFalse(self.state.more_input)

        self.command.process(Mode.Normal, self.state)

        self.assertTrue(self.state.more_input)

    def test_RequestsMoreInputIfNoSecondKeyAvailable(self):
        self.assertFalse(self.state.more_input)

        self.state.append('"')

        self.command.process(Mode.Normal, self.state)

        self.assertTrue(self.state.more_input)

    def test_RequestsMoreInputIfNoSecondKeyAvailableSingleQuote(self):
        self.assertFalse(self.state.more_input)

        self.state.append("'")

        self.command.process(Mode.Normal, self.state)

        self.assertTrue(self.state.more_input)

    def test_RequestsMoreInputIfNoSecondKeyAvailableParenthesis(self):
        self.assertFalse(self.state.more_input)

        self.state.append("[")

        self.command.process(Mode.Normal, self.state)

        self.assertTrue(self.state.more_input)

    def test_RequestsMoreInputIfNoSecondKeyAvailableCurlyBracket(self):
        self.assertFalse(self.state.more_input)

        self.state.append("(")

        self.command.process(Mode.Normal, self.state)

        self.assertTrue(self.state.more_input)

    def test_RequestsMoreInputIfNoSecondKeyAvailableSquaredBracket(self):
        self.assertFalse(self.state.more_input)

        self.state.append("{")

        self.command.process(Mode.Normal, self.state)

        self.assertTrue(self.state.more_input)

    def test_RaisesErrorIfUnknownDelimiter(self):
        self.assertFalse(self.state.more_input)

        self.state.append('?')

        def fail():
            self.command.process(Mode.Normal, self.state)

        self.assertRaises(AbortCommandError, fail)

    def test_SetsFirstKey(self):
        self.assertFalse(self.state.more_input)

        self.state.append('"')
        self.command.process(Mode.Normal, self.state)

        self.assertEquals('"', self.command.old)

    def test_SetsSecondKey(self):
        self.assertFalse(self.state.more_input)

        self.state.append('"')
        self.state.append("'")
        self.command.process(Mode.Normal, self.state)

        self.assertEquals("'", self.command.new)


class Test_reset(TestSurroundChangeSixPluginBase):

    def testResetsInternalData(self):
        self.state.append("'")
        self.state.append('"')

        self.command.process(Mode.Normal, self.state)
        self.command.reset()

        self.assertIsNone(self.command.old)
        self.assertIsNone(self.command.new)
