import sys
import os
import unittest

sys.path.append(os.path.join(os.getcwd(), '..'))
from common.variables import *
from client import create_presence, process_ans


class TestClientClass(unittest.TestCase):

    def test_create_presence_dic(self):
        self.assertIsInstance(create_presence(), dict)

    def test_create_presence_answer(self):
        test = create_presence('test')
        test[TIME] = 11
        self.assertEqual(test, {'action': 'presence', 'time': 11, 'user': {'account_name': 'test'}})

    def test_process_ans_ok(self):
        self.assertIn('200', process_ans({RESPONSE: 200}))

    def test_process_ans_error_code(self):
        self.assertEqual(process_ans({RESPONSE: 401, ERROR: 'Not auth'}), 'HTTP/1.1: 400 401. Not auth')

    def test_process_ans_exception(self):
        self.assertRaises(ValueError, process_ans, 'error')


if __name__ == '__main__':
    unittest.main()
