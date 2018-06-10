import unittest

import sublime

from Six.lib.command_state import CommandState
from Six.lib.constants import Mode
from Six.lib.yank_registers import EditOperation
from User.six.surround import surround


class ViewTest(unittest.TestCase):

    def setUp(self):
        self.window = sublime.active_window()
        self.view = self.window.new_file()
        self.view.set_scratch(True)

    def tearDown(self):
        self.window.run_command('close')


class Test_SurroundChangeSixPlugin(unittest.TestCase):

    def setUp(self):
        cls = surround(register=False)
        self.command = cls()

    def test___init__(self):
        self.assertEquals("zs", self.command.name)
        self.assertEquals(EditOperation.Other, self.command.kind)
        self.assertIsNone(self.command.old)
        self.assertIsNone(self.command.new)

    def test_stateAtEofLeadsToMoreInputRequested(self):
        state = CommandState()

        self.assertFalse(state.more_input)

        self.command.process(Mode.Normal, state)

        self.assertTrue(state.more_input)
