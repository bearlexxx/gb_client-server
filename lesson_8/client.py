""" Клиент """

import argparse
import json
import sys
import time
from socket import socket, AF_INET, SOCK_STREAM
from threading import Thread
from common.utils import get_message, send_message
from common.variables import DEFAULT_PORT, DEFAULT_IP_ADDRESS, ACTION, USER, ACCOUNT_NAME, TIME, RESPONSE, ERROR, \
    PRESENCE, MESSAGE, MESSAGE_TEXT, SENDER, DESTINATION, EXIT
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
    to_user = input(f'Введите ник получателя: ')
    message = input(f'Введите сообщение для отправки: ')
    message_dict = {
        ACTION: MESSAGE,
        SENDER: account_name,
        DESTINATION: to_user,
        TIME: time.time(),
        MESSAGE_TEXT: message
    }

    if __debug__:
        log.debug(f'Сформирован словарь сообщения: {message_dict}')

    try:
        send_message(sock, message_dict)
        log.info(f'Сообщение отправлено от {account_name} для {to_user}')
    except Exception as error:
        print(error)
        log.critical(f'Потеряно соединение с сервером')
        sys.exit(1)


@logs
def arg_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('addr', default=DEFAULT_IP_ADDRESS, nargs='?')
    parser.add_argument('port', default=DEFAULT_PORT, type=int, nargs='?')
    parser.add_argument('-n', '--name', default=None, nargs='?')
    args = parser.parse_args(sys.argv[1:])
    server_address = args.addr
    server_port = args.port
    client_name = args.name

    if args.port < 1024 or args.port > 65536:
        log.warning(f'Диапозон номера порта от 1024 до 65635')
        sys.exit(1)

    return server_address, server_port, client_name


@logs
def create_exit_message(account_name):
    return {
        ACTION: EXIT,
        TIME: time.time(),
        ACCOUNT_NAME: account_name
    }


def print_help():
    print('Поддерживаемые команды:')
    print('message - отправить сообщение. Кому и текст будет запрошены отдельно.')
    print('help - вывести подсказки по командам')
    print('exit - выход из программы')


@logs
def message_from_server(sock, my_username):
    while True:
        try:
            message = get_message(sock)
            if ACTION in message and message[ACTION] == MESSAGE and \
                    SENDER in message and DESTINATION in message \
                    and MESSAGE_TEXT in message and message[DESTINATION] == my_username:
                print(f'\nПолучено сообщение от пользователя {message[SENDER]}:'
                      f'\n{message[MESSAGE_TEXT]}')
                log.info(f'Получено сообщение от пользователя {message[SENDER]}:'
                         f'\n{message[MESSAGE_TEXT]}')
            else:
                log.error(f'Получено некорректное сообщение с сервера: {message}')
        except Exception as error:
            log.error(f'{error}')
        except (OSError, ConnectionError, ConnectionAbortedError,
                ConnectionResetError, json.JSONDecodeError):
            log.critical(f'Потеряно соединение с сервером.')
            break


@logs
def user_interactive(sock, username):
    print_help()
    while True:
        command = input('Введите команду: ')
        if command == 'message':
            create_message(sock, username)
        elif command == 'help':
            print_help()
        elif command == 'exit':
            send_message(sock, create_exit_message(username))
            print(f'Завершение соединения.')
            log.info(f'Завершение работы по команде пользователя.')
            time.sleep(0.5)
            break
        else:
            print(f'Неизвестное сообщение. Список поддерживаемых команд: help')


def main():
    server_address, server_port, client_name = arg_parser()
    print(f'Имя пользователя: {client_name}')

    if not client_name:
        client_name = input('Введите имя пользователя: ')

    log.info(f'Запущен клиент с параметрами: \n'
             f'адрес сервера: {server_address}, порт: {server_port}, имя пользователя: {client_name}')

    try:
        transport = socket(AF_INET, SOCK_STREAM)
        transport.connect((server_address, server_port))
        send_message(transport, create_presence(client_name))
        answer = process_ans(get_message(transport))
        log.info(f'Установлено соединение с сервером. Ответ сервера: {answer}')
        print(f'Установлено соединение с сервером.')
    except json.JSONDecodeError:
        log.error('Не удалось декодировать полученную Json строку.')
        sys.exit(1)
    except Exception as error:
        log.error(f'{error}')
        sys.exit(1)
    except (ConnectionRefusedError, ConnectionError):
        log.critical(f'Не удалось подключиться к серверу {server_address}:{server_port} ')
        sys.exit(1)
    else:
        receiver = Thread(target=message_from_server, args=(transport, client_name))
        receiver.daemon = True
        receiver.start()

        user_interface = Thread(target=user_interactive, args=(transport, client_name))
        user_interface.daemon = True
        user_interface.start()
        log.debug('Запущены процессы')

        while True:
            time.sleep(1)
            if receiver.is_alive() and user_interface.is_alive():
                continue
            break


if __name__ == '__main__':
    main()
