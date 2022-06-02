""" Клиент """

import json
import sys
import time
from socket import socket, AF_INET, SOCK_STREAM
from common.utils import get_message, send_message
from common.variables import DEFAULT_PORT, DEFAULT_IP_ADDRESS, ACTION, USER, ACCOUNT_NAME, TIME, RESPONSE, ERROR, \
    PRESENCE


def create_presence(account_name='Guest'):
    msg = {
        ACTION: PRESENCE,
        TIME: time.time(),
        USER: {
            ACCOUNT_NAME: account_name
        }
    }

    return msg


def process_ans(message):
    if RESPONSE in message:
        if message[RESPONSE] == 200:
            return 'HTTP/1.1: 200 OK'
        return f'HTTP/1.1: 400 {message[RESPONSE]}. {message[ERROR]}'
    return ValueError


def main():
    try:
        server_addr = sys.argv[1]
        server_port = int(sys.argv[2])
        if server_port < 1024 or server_port > 65536:
            raise ValueError
    except IndexError:
        print(f'Без указания адреса и порта применяются настройки по умолчанию'
              f' {DEFAULT_IP_ADDRESS}:{DEFAULT_PORT}')
        server_addr = DEFAULT_IP_ADDRESS
        server_port = DEFAULT_PORT
    except ValueError:
        print('Диапозон номера порта от 1024 до 65635')
        sys.exit(1)

    s = socket(AF_INET, SOCK_STREAM)
    s.connect((server_addr, server_port))
    msg_out = create_presence('Guest')
    try:
        send_message(s, msg_out)
    except TypeError:
        print('Ошибка сообщения')

    try:
        msg_in = get_message(s)
        print(process_ans(msg_in))
    except(ValueError, json.JSONDecodeError):
        print('Некорректное сообщение')


if __name__ == '__main__':
    main()
