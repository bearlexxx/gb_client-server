""" Сервер """

import argparse
import sys
import time
from socket import socket, AF_INET, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR
import json
from select import select
from common.variables import DEFAULT_PORT, MAX_CONNECTIONS, ACTION, USER, ACCOUNT_NAME, TIME, RESPONSE, ERROR, \
    PRESENCE, CONNECTION_TIMEOUT, MESSAGE, MESSAGE_TEXT, SENDER, DESTINATION, EXIT
from common.utils import get_message, send_message
import logging
import logs.server_log_config
from common.decorators import logs

log = logging.getLogger('app.server')


@logs
def process_client_message(message, messages_list, client, clients, names):
    if ACTION in message and message[ACTION] == PRESENCE and TIME in message and USER in message:

        if message[USER][ACCOUNT_NAME] not in names.keys():
            names[message[USER][ACCOUNT_NAME]] = client
            send_message(client, {RESPONSE: 200, ERROR: 'HTTP/1.1: 200 OK '})
        else:
            send_message(client, {RESPONSE: 400, ERROR: 'Такой ник уже используется'})
            clients.remove(client)
            client.close()
        return

    elif ACTION in message and message[ACTION] == MESSAGE and DESTINATION in message and TIME in message \
            and SENDER in message and MESSAGE_TEXT in message:
        messages_list.append(message)
        return

    elif ACTION in message and message[ACTION] == EXIT and ACCOUNT_NAME in message:
        clients.remove(names[message[ACCOUNT_NAME]])
        names[message[ACCOUNT_NAME]].close()
        del names[message[ACCOUNT_NAME]]
        return

    else:
        send_message(client, {RESPONSE: 400, ERROR: 'HTTP/1.1: Error 400 Bad request'})
        return True



@logs
def process_message(message, names, listen_socks):
    if message[DESTINATION] in names and names[message[DESTINATION]] in listen_socks:
        send_message(names[message[DESTINATION]], message)
        log.info(f'Отправлено сообщение от {message[SENDER]} для пользователя {message[DESTINATION]}')
    elif message[DESTINATION] in names and names[message[DESTINATION]] not in listen_socks:
        raise ConnectionError
    else:
        log.error(f'Пользователь {message[DESTINATION]} не зарегистрирован на сервере')


@logs
def arg_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', default=DEFAULT_PORT, type=int, nargs='?')
    parser.add_argument('-a', default='', nargs='?')
    args = parser.parse_args(sys.argv[1:])
    listen_address = args.a
    listen_port = args.p

    if not 1023 < listen_port < 65536:
        log.warning(f'Диапозон номера порта от 1024 до 65635')
        sys.exit(1)

    return listen_address, listen_port


def main():
    listen_address, listen_port = arg_parser()
    all_clients = []
    messages = []

    with socket(AF_INET, SOCK_STREAM) as s:
        s.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        s.bind((listen_address, listen_port))
        s.listen(MAX_CONNECTIONS)
        s.settimeout(CONNECTION_TIMEOUT)
        print(f'Server ready. Listen connect on {listen_address}:{listen_port}')
        log.info(f'Server start. Listen connect on {listen_address}:{listen_port}')

        clients = []
        names = dict()

        while True:
            try:
                client_socket, client_address = s.accept()
            except OSError:
                pass
            else:
                log.info(f'Получен запрос на соединение от {str(client_address)}')
                print(f"Получен запрос на соединение от {str(client_address)}")
                all_clients.append(client_socket)

            wait = 0.1
            clients_read = []
            clients_write = []

            if all_clients:
                try:
                    clients_read, clients_write, errors = select(all_clients, all_clients, [], wait)
                except OSError:
                    pass
                except Exception as e:
                    print('ошибка в select:', e)

            if clients_read:
                for client_with_message in clients_read:
                    try:
                        process_client_message(get_message(client_with_message), messages, client_with_message, clients,
                                               names)
                    except OSError:
                        print('Клиент отключился')
                        log.info(f'Клиент отключился от сервера.')
                        all_clients.remove(client_with_message)
                        client_with_message.close()
                    except Exception as e:
                        print('Клиент отключился', client_with_message.getpeername())
                        log.info(f'Клиент {client_with_message.getpeername()} отключился от сервера.')
                        all_clients.remove(client_with_message)
                        client_with_message.close()

            for i in messages:
                try:
                    process_message(i, names, clients_write)
                except Exception:
                    log.info(f'Связь с клиентом с ником {i[DESTINATION]} была потеряна')
                    clients.remove(names[i[DESTINATION]])
                    del names[i[DESTINATION]]
        messages.clear()


if __name__ == '__main__':
    main()
