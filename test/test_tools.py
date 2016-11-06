# -*- coding: utf-8 -*-

import json
import unittest
import subprocess as sp
from mock import patch

import tools


class ToolsTest(unittest.TestCase):

    @patch('tools.execute')
    def test_get_game(self, exe):
        expected = {'one': 1, 'two': 2}
        exe.return_value = json.dumps(expected)
        actual = tools.get_game('1234')
        self.assertEquals(actual, expected)
