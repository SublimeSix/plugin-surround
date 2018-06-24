import unittest
from unittest import mock

import sublime

from sublime import Region as R

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


class TestSurroundSixPluginBase(unittest.TestCase):

    def setUp(self):
        super().setUp()
        cls = surround(register=False)[self.plugin_name]
        self.command = cls()
        self.state = CommandState()


class TestSurroundChangeSixPluginBase(TestSurroundSixPluginBase):

    def setUp(self):
        self.plugin_name = "CSurround"
        super().setUp()


class Test__init__(TestSurroundChangeSixPluginBase):

    def test__init__(self):
        self.assertEquals("CSurround", self.command.name)
        self.assertEquals(EditOperation.Other, self.command.kind)
        self.assertIsNone(self.command.old)
        self.assertIsNone(self.command.new)


class TestSurroundChangeSixPlugin_process(TestSurroundChangeSixPluginBase):

    def testRequestsMoreInputIfNoInputAvailable(self):
        self.assertFalse(self.state.more_input)

        self.command.process(Mode.Normal, self.state)

        self.assertTrue(self.state.more_input)

    def testRequestsMoreInputIfNoSecondKeyAvailableDoubleQuote(self):
        self.assertFalse(self.state.more_input)

        self.state.append('"')

        self.command.process(Mode.Normal, self.state)

        self.assertTrue(self.state.more_input)

    def testRequestsMoreInputIfNoSecondKeyAvailableSingleQuote(self):
        self.assertFalse(self.state.more_input)

        self.state.append("'")

        self.command.process(Mode.Normal, self.state)

        self.assertTrue(self.state.more_input)

    def testRequestsMoreInputIfNoSecondKeyAvailableParenthesis(self):
        self.assertFalse(self.state.more_input)

        self.state.append("(")

        self.command.process(Mode.Normal, self.state)

        self.assertTrue(self.state.more_input)

    def testRequestsMoreInputIfNoSecondKeyAvailableCurlyBracket(self):
        self.assertFalse(self.state.more_input)

        self.state.append("{")

        self.command.process(Mode.Normal, self.state)

        self.assertTrue(self.state.more_input)

    def testRequestsMoreInputIfNoSecondKeyAvailableSquaredBracket(self):
        self.assertFalse(self.state.more_input)

        self.state.append("[")

        self.command.process(Mode.Normal, self.state)

        self.assertTrue(self.state.more_input)

    def testRaisesErrorIfUnknownDelimiter(self):
        self.assertFalse(self.state.more_input)

        self.state.append('?')

        def fail():
            self.command.process(Mode.Normal, self.state)

        self.assertRaises(AbortCommandError, fail)

    def testSetsFirstKey(self):
        self.assertFalse(self.state.more_input)

        self.state.append('"')
        self.command.process(Mode.Normal, self.state)

        self.assertEquals('"', self.command.old)

    def testSetsSecondKey(self):
        self.assertFalse(self.state.more_input)

        self.state.append('"')
        self.state.append("'")
        self.command.process(Mode.Normal, self.state)

        self.assertEquals("'", self.command.new)


class TestSurroundChangeSixPlugin_reset(TestSurroundChangeSixPluginBase):

    def testResetsInternalData(self):
        self.state.append("'")
        self.state.append('"')

        self.command.process(Mode.Normal, self.state)
        self.command.reset()

        self.assertIsNone(self.command.old)
        self.assertIsNone(self.command.new)


class TestSurroundSixPluginChange_execute(TestSurroundChangeSixPluginBase, ViewTest):

    def testCanExecute(self):
        self.view.run_command("append", { "characters": "aaa (bbb) ccc" })
        self.view.sel().clear()
        self.view.sel().add(R(5))

        self.assertEquals("(", self.view.substr(4))
        self.assertEquals(")", self.view.substr(8))

        self.command.old = "("
        self.command.new = "]"
        self.command.execute()

        self.assertEquals("[", self.view.substr(4))
        self.assertEquals("]", self.view.substr(8))

    def testDoesNotExecuteForIdenticalBracket(self):
        self.view.run_command("append", { "characters": "aaa (bbb) ccc" })
        self.view.sel().clear()
        self.view.sel().add(R(5))

        self.assertEquals("(", self.view.substr(4))
        self.assertEquals(")", self.view.substr(8))

        self.command.old = "("
        self.command.new = ")"
        self.command.execute()

        self.assertEquals("(", self.view.substr(4))
        self.assertEquals(")", self.view.substr(8))


class TestSurroundDeleteSixPluginBase(TestSurroundSixPluginBase):

    def setUp(self):
        self.plugin_name = "DSurround"
        super().setUp()


class TestSurroundSixPluginDelete__init__(TestSurroundDeleteSixPluginBase):

    def testCanInit(self):
        self.assertEquals(self.command.name, "DSurround")
        self.assertIsNone(self.command.old)
        self.assertEquals(self.command.kind, EditOperation.Other)


class TestSurroundSixPluginDelete_reset(TestSurroundDeleteSixPluginBase):

    def testCanReset(self):
        self.assertIsNone(self.command.old)

        self.command.old = "'"
        self.command.reset()

        self.assertIsNone(self.command.old)


class TestSurroundSixPluginDelete_process(TestSurroundDeleteSixPluginBase):

    def testRequestsMoreInputIfNoInputAvailable(self):
        self.assertFalse(self.state.more_input)

        self.command.process(Mode.Normal, self.state)

        self.assertTrue(self.state.more_input)

    def testDoNotRequestsMoreInputIfKeyAvailableDoubleQuote(self):
        self.assertFalse(self.state.more_input)

        self.state.append('"')

        self.command.process(Mode.Normal, self.state)

        self.assertFalse(self.state.more_input)

    def testDoNotRequestsMoreInputIfKeyAvailableSingleQuote(self):
        self.assertFalse(self.state.more_input)

        self.state.append("'")

        self.command.process(Mode.Normal, self.state)

        self.assertFalse(self.state.more_input)

    def testDoNotRequestsMoreInputIfKeyAvailableParenthesis(self):
        self.assertFalse(self.state.more_input)

        self.state.append("(")

        self.command.process(Mode.Normal, self.state)

        self.assertFalse(self.state.more_input)

    def testDoNotRequestsMoreInputIfKeyAvailableCurlyBracket(self):
        self.assertFalse(self.state.more_input)

        self.state.append("{")

        self.command.process(Mode.Normal, self.state)

        self.assertFalse(self.state.more_input)

    def testDoNotRequestsMoreInputIfKeyAvailableSquaredBracket(self):
        self.assertFalse(self.state.more_input)

        self.state.append("[")

        self.command.process(Mode.Normal, self.state)

        self.assertFalse(self.state.more_input)

    def testRaisesErrorIfUnknownDelimiter(self):
        self.assertFalse(self.state.more_input)

        self.state.append('?')

        def fail():
            self.command.process(Mode.Normal, self.state)

        self.assertRaises(AbortCommandError, fail)

    def testSetsFirstKey(self):
        self.assertFalse(self.state.more_input)

        self.state.append('"')
        self.command.process(Mode.Normal, self.state)

        self.assertEquals('"', self.command.old)


class TestSurroundSixPluginDelete_execute(TestSurroundDeleteSixPluginBase, ViewTest):

    def testCanExecute(self):
        self.view.run_command("append", { "characters": "aaa (bbb) ccc" })
        self.view.sel().clear()
        self.view.sel().add(R(5))

        self.assertEquals("(", self.view.substr(4))
        self.assertEquals(")", self.view.substr(8))

        self.command.old = "("
        self.command.execute()

        self.assertEquals("b", self.view.substr(4))
        self.assertEquals(" ", self.view.substr(7))
