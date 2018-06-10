import unittest

import sublime

from sublime import Region as R


class ViewTest(unittest.TestCase):

    def setUp(self):
        self.window = sublime.active_window()
        self.view = self.window.new_file()
        self.view.set_scratch(True)

    def tearDown(self):
        self.window.run_command('close')


class Test_one(ViewTest):

    def testOne(self):
        self.view.run_command('append', {'characters': 'some "text" here'})
        self.view.sel().clear()
        self.view.sel().add(R(6))

        self.assertEquals(7, self.view.sel()[0].b)
