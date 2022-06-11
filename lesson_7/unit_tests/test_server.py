import sys
import os
import unittest

sys.path.append(os.path.join(os.getcwd(), '..'))
from common.variables import *
from server import process_client_message


class TestServerClass(unittest.TestCase):

    def test_is_dict(self):
        self.assertIsInstance(process_client_message({}), dict)
        self.assertIsInstance(process_client_message(' '), dict)

    def test_required_fields(self):
        test = process_client_message({ACTION: PRESENCE})
        self.assertEqual(test, {RESPONSE: 400, ERROR: 'Bad request'})
        test = process_client_message({TIME: 10})
        self.assertEqual(test, {RESPONSE: 400, ERROR: 'Bad request'})

    def test_account_name(self):
        test = process_client_message({ACTION: PRESENCE, TIME: 11,
                                       USER:{ACCOUNT_NAME: 'test'}
                                       })
        self.assertEqual(test[RESPONSE], 401)

        test = process_client_message({ACTION: PRESENCE, TIME: 11,
                                       USER: {ACCOUNT_NAME: 'Guest'}
                                       })
        self.assertEqual(test[RESPONSE], 200)

    def test_unknown_action(self):
        test = process_client_message({ACTION: 'unknown', TIME: 55})
        self.assertEqual(test[RESPONSE], 400)

if __name__ == '__main__':
    unittest.main()
