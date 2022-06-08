import json
import sys
import os
import unittest

sys.path.append(os.path.join(os.getcwd(), '..'))
from common.variables import *
from common.utils import *


class TestSocket:

    def __init__(self, test_dict):
        self.test_dict = test_dict
        self.encoded_msg = None
        self.received_msg = None

    def send(self, msg):
        json_test_msg = json.dumps(self.test_dict)
        self.encoded_msg = json_test_msg.encode(ENCODING)
        self.received_msg = msg

    def recv(self, max_len):
        json_test_msg = json.dumps(self.test_dict)
        return json_test_msg.encode(ENCODING)


class TestClientClass(unittest.TestCase):

    test_dict_send = {ACTION: PRESENCE, TIME: 122.33, USER: {ACCOUNT_NAME: 'test'}}
    test_dict_recv_ok = {RESPONSE: 200}
    test_dict_recv_error = {RESPONSE: 400, ERROR: 'Bad Request'}

    def test_send_message_ok(self):
        test_socket = TestSocket(self.test_dict_send)
        send_message(test_socket, self.test_dict_send)
        self.assertEqual(test_socket.received_msg, test_socket.encoded_msg)

    def test_send_message_exception(self):
        test_socket = TestSocket(self.test_dict_send)
        self.assertRaises(TypeError, send_message, test_socket, 'error')

    def test_get_message_ok(self):
        test_socket = TestSocket(self.test_dict_recv_ok)
        self.assertEqual(get_message(test_socket), self.test_dict_recv_ok)

    def test_get_message_error(self):
        test_socket = TestSocket(self.test_dict_recv_error)
        self.assertEqual(get_message(test_socket), self.test_dict_recv_error)


if __name__ == '__main__':
    unittest.main()
