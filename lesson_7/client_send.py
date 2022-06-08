""" Клиент """
# Только прием сообщений
import argparse
import json
import sys
import time
from socket import socket, AF_INET, SOCK_STREAM
from common.utils import get_message, send_message
from common.variables import DEFAULT_PORT, DEFAULT_IP_ADDRESS, ACTION, USER, ACCOUNT_NAME, TIME, RESPONSE, ERROR, \
    PRESENCE, MESSAGE, MESSAGE_TEXT, SENDER
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
    elif ACTION in message:
        if message[ACTION] == MESSAGE and SENDER in message and MESSAGE_TEXT in message:
            print(f'Получено сообщение от пользователя '
                  f'{message[SENDER]}:\n{message[MESSAGE_TEXT]}')
            log.info(f'Получено сообщение от пользователя '
                     f'{message[SENDER]}:\n{message[MESSAGE_TEXT]}')
            return True
    log.error(f'Error {RESPONSE}')
    raise ValueError


@logs
def create_message(sock, account_name='Guest'):
    message = input('Введите сообщение для отправки или "!!!" для завершения работы: ')
    if message == '!!!':
        sock.close()
        log.info('Завершение работы по команде пользователя.')
        print('До свидания')
        time.sleep(2)
        sys.exit(0)

    message_dict = {
        ACTION: MESSAGE,
        TIME: time.time(),
        ACCOUNT_NAME: account_name,
        MESSAGE_TEXT: message
    }

    if __debug__:
        log.debug(f'Сформирован словарь сообщения: {message_dict}')

    return message_dict


@logs
def arg_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('addr', default=DEFAULT_IP_ADDRESS, nargs='?',
                        help=f'Server address. Default {DEFAULT_IP_ADDRESS}')
    parser.add_argument('port', default=DEFAULT_PORT, type=int, nargs='?',
                        help=f'Server port 1024-65535. Default {DEFAULT_PORT}')
    parser.add_argument('-m', '--mode', default='send', nargs='?', help='send or listen mode')
    args = parser.parse_args()

    if args.port < 1024 or args.port > 65536:
        log.warning(f'Диапозон номера порта от 1024 до 65635')
        sys.exit(1)

    return args.addr, args.port, args.mode


def main():
    server_address, server_port, client_mode = arg_parser()

    if client_mode != 'send' and client_mode != 'listen':
        log.warning('Указанный режим работы не поддерживается! Укажите send или listen')
        sys.exit(1)

    log.info(f'Клиент запущен со следующими параметрами:'
             f' {DEFAULT_IP_ADDRESS}:{DEFAULT_PORT}, Mode: {client_mode}')

    try:
        s = socket(AF_INET, SOCK_STREAM)
        s.connect((server_address, server_port))
    except ConnectionRefusedError:
        log.critical(
            f'Не удалось подключиться к серверу {server_address}:{server_port}, '
            f'конечный компьютер отверг запрос на подключение.')
        sys.exit(1)

    try:
        msg_out = create_presence('Guest')
        send_message(s, msg_out)

        msg_in = get_message(s)
        print(process_ans(msg_in))
    except TypeError as e:
        log.critical(e)
        s.close()
        sys.exit(1)
    except(ValueError, json.JSONDecodeError) as e:
        log.error(e)
        s.close()
        sys.exit(1)

    if client_mode == 'send':
        print('Режим отправки сообщений.')
        while True:
            try:
                msg_out = create_message(s)
                send_message(s, msg_out)
            except (ConnectionResetError, ConnectionError, ConnectionAbortedError):
                log.error(f'Соединение с сервером {server_address} было потеряно.')
                sys.exit(1)

    else:
        print('Режим приема сообщений.')
        while True:
            try:
                process_ans(get_message(s))
            except (ConnectionResetError, ConnectionError, ConnectionAbortedError):
                log.error(f'Соединение с сервером {server_address} было потеряно.')
                sys.exit(1)


if __name__ == '__main__':
    main()
