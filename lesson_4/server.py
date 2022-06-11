""" Сервер """

import sys
from socket import socket, AF_INET, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR
import json
from common.variables import DEFAULT_PORT, MAX_CONNECTIONS, ACTION, USER, ACCOUNT_NAME, TIME, RESPONSE, ERROR, \
    PRESENCE
from common.utils import get_message, send_message


def process_client_message(message):
    if ACTION not in message or TIME not in message:
        return {RESPONSE: 400, ERROR: 'Bad request'}

    if message[ACTION] == PRESENCE:
        if message[USER][ACCOUNT_NAME] == 'Guest':
            return {RESPONSE: 200}
        else:
            return {RESPONSE: 401, ERROR: f'Not authorize account {message[USER][ACCOUNT_NAME]}'}
    else:
        return {RESPONSE: 400, ERROR: f'Action {message[ACTION]} not support'}


def main():
    try:
        if '-p' in sys.argv:
            listen_port = int(sys.argv[sys.argv.index('-p') + 1])
        else:
            listen_port = DEFAULT_PORT
        if listen_port < 1024 or listen_port > 65536:
            raise ValueError
    except IndexError:
        print(f'После параметра -p необходимо указать номер порта, по умолчанию: {DEFAULT_PORT}')
        sys.exit(1)
    except ValueError:
        print('Диапозон номера порта от 1024 до 65635')
        sys.exit(1)

    # tcp address
    try:
        if '-a' in sys.argv:
            listen_address = sys.argv[sys.argv.index('-a') + 1]
        else:
            listen_address = ''
    except IndexError:
        print(f'После параметра -a необходимо указать ip адрес')
        sys.exit(1)

    s = socket(AF_INET, SOCK_STREAM)
    s.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    s.bind((listen_address, listen_port))
    s.listen(MAX_CONNECTIONS)

    try:
        while True:
            client_socket, client_address = s.accept()
            try:
                msg_in = get_message(client_socket)
                print(msg_in)
                msg_out = process_client_message(msg_in)
                send_message(client_socket, msg_out)
            except(ValueError, json.JSONDecodeError):
                print('Некорректное сообщение')
            except TypeError:
                print('Ошибка сообщения')
            finally:
                client_socket.close()
    finally:
        s.close()


if __name__ == '__main__':
    main()
