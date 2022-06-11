""" Сервер """
import argparse
import sys
import time
from socket import socket, AF_INET, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR
import json
from select import select
from common.variables import DEFAULT_PORT, MAX_CONNECTIONS, ACTION, USER, ACCOUNT_NAME, TIME, RESPONSE, ERROR, \
    PRESENCE, CONNECTION_TIMEOUT, MESSAGE, MESSAGE_TEXT, SENDER
from common.utils import get_message, send_message
import logging
import logs.server_log_config
from common.decorators import logs

log = logging.getLogger('app.server')


@logs
def process_client_message(message, messages_list, sock):
    if ACTION not in message or TIME not in message:
        if __debug__:
            log.warning(f'Bad request.  {message}')
        return {RESPONSE: 400, ERROR: 'Bad request'}

    if message[ACTION] == PRESENCE:
        if message[USER][ACCOUNT_NAME] == 'Guest':
            if __debug__:
                log.debug(f'HTTP/1.1: 200 OK :: {PRESENCE}::')
            send_message(sock, {RESPONSE: 200})
            return True
        else:
            if __debug__:
                log.debug(f'HTTP/1.1: 401 Unauthorized Error')
            send_message(sock, {RESPONSE: 401, ERROR: f'Not authorize account {message[USER][ACCOUNT_NAME]}'})
            return True
    elif message[ACTION] == MESSAGE and MESSAGE_TEXT in message:
        messages_list.append((message[ACCOUNT_NAME], message[MESSAGE_TEXT]))
        if __debug__:
            log.info(f'HTTP/1.1: Error 400 Bad request. {ACTION} not support')
        send_message(sock, {RESPONSE: 400, ERROR: f'Action {message[ACTION]} not support'})
        return True


@logs
def read_requests(read_clients, all_clients):
    requests = {}

    for sock in read_clients:
        try:
            msg_in = get_message(sock)
            requests[sock] = msg_in
        except json.JSONDecodeError as e:
            log.warning(f'Ошибка парсинга JSON: {e}')
        except ValueError as e:
            log.warning(f'Принято некорректное сообщение или Клиент {sock.fileno()} {sock.getpeername()} отключился')
            sock.close()
            all_clients.remove(sock)
        except ConnectionResetError as e:
            log.warning(f'Клиент закрыл соединение! Сокет отключен')
            sock.close()
            all_clients.remove(sock)

    return requests


@logs
def write_responses(requests, clients_write, all_clients):
    for sock in clients_write:
        if sock in requests:
            try:
                if requests[sock] == '':
                    raise ValueError
                msg_in = requests[sock]
                msg_out = process_client_message(msg_in, [])
                send_message(sock, msg_out)
            except TypeError:
                log.error(f'Для отправки сообщения нужен словарь с данными. Не отправилось: {msg_out}')
            except Exception as e:
                all_clients.remove(sock)
                sock.close()


@logs
def arg_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('-a', default='', nargs='?',
                        help=f'Server address. Default - all net interfaces')
    parser.add_argument('-p', default=DEFAULT_PORT, type=int, nargs='?',
                        help=f'Server port 1024-65535. Default {DEFAULT_PORT}')
    args = parser.parse_args()

    if not 1023 < args.p < 65536:
        log.warning(f'Диапозон номера порта от 1024 до 65635')
        sys.exit(1)

    return args.a, args.p


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

        while True:
            try:
                client_socket, client_address = s.accept()
            except OSError as err:
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
                        print(f'пришло сообщение от {client_with_message.getpeername()}')
                        process_client_message(get_message(client_with_message), messages, client_with_message)
                    except OSError:
                        print('Отправитель отключился')
                        log.info(f'Отправитель отключился от сервера.')
                        all_clients.remove(client_with_message)
                        client_with_message.close()
                    except Exception as e:
                        print('Отправитель отключился', client_with_message.getpeername())
                        log.info(f'Отправитель {client_with_message.getpeername()} отключился от сервера.')
                        all_clients.remove(client_with_message)
                        client_with_message.close()

            if clients_write and messages:
                for _ in range(len(messages)):
                    msg = messages.pop()

                    message = {
                        ACTION: MESSAGE,
                        SENDER: msg[0],
                        TIME: time.time(),
                        MESSAGE_TEXT: msg[1]
                    }

                    for waiting_client in clients_write:
                        try:
                            print('отправили сообщение', waiting_client, message)
                            send_message(waiting_client, message)
                        except:
                            log.info(f'Клиент  отключился от сервера.')
                            waiting_client.close()
                            all_clients.remove(waiting_client)


if __name__ == '__main__':
    main()
