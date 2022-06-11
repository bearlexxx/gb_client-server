""" Клиент """

import json
import sys
import time
from socket import socket, AF_INET, SOCK_STREAM
from common.utils import get_message, send_message
from common.variables import DEFAULT_PORT, DEFAULT_IP_ADDRESS, ACTION, USER, ACCOUNT_NAME, TIME, RESPONSE, ERROR, \
    PRESENCE
import logging
import logs.client_log_config
from common.decorators import logs

log = logging.getLogger('app.client')


@logs
def create_presence(account_name='Guest'):
    msg = {
        ACTION: PRESENCE,
        TIME: time.time(),
        USER: {
            ACCOUNT_NAME: account_name
        }
    }

    if __debug__:
        log.debug(f'Socket created. Account name: {account_name}')

    return msg


@logs
def process_ans(message):
    if RESPONSE in message:
        if message[RESPONSE] == 200:
            if __debug__:
                log.debug(f'HTTP/1.1: 200 OK  :: {message[RESPONSE]} ::')
            return 'HTTP/1.1: 200 OK'
        log.error(f'HTTP/1.1: 400 Bad request. :: {message[RESPONSE]}:: {message[ERROR]}')
        return f'HTTP/1.1: 400 Bad request. :: {message[RESPONSE]}:: {message[ERROR]}'
    log.error(f'Error {RESPONSE}')
    raise ValueError


def main():
    try:
        server_addr = sys.argv[1]
        server_port = int(sys.argv[2])
        if server_port < 1024 or server_port > 65536:
            raise ValueError
    except IndexError:
        log.warning(f'Без указания адреса и порта применяются настройки по умолчанию'
                    f' {DEFAULT_IP_ADDRESS}:{DEFAULT_PORT}')
        server_addr = DEFAULT_IP_ADDRESS
        server_port = DEFAULT_PORT
    except ValueError:
        log.warning('Диапозон номера порта от 1024 до 65635')
        sys.exit(1)

    s = socket(AF_INET, SOCK_STREAM)
    s.connect((server_addr, server_port))
    msg_out = create_presence('Guest')
    try:
        send_message(s, msg_out)
    except TypeError:
        log.critical('Ошибка сообщения')

    try:
        msg_in = get_message(s)
        print(process_ans(msg_in))
    except(ValueError, json.JSONDecodeError):
        log.error('Некорректное сообщение')


if __name__ == '__main__':
    main()
