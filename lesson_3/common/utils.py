import json
from variables import MAX_PACKET_LENGTH, ENCODING


def get_message(client):
    data_bytes = client.recv(MAX_PACKET_LENGTH)
    if not isinstance(data_bytes, bytes):
        raise ValueError

    data_str = data_bytes.decode(ENCODING)
    if not isinstance(data_str, str):
        raise ValueError

    data_dict = json.loads(data_str)
    if not isinstance(data_dict, dict):
        raise ValueError

    return data_dict


def send_message(sock, message):
    if not isinstance(message, dict):
        raise TypeError

    message_bytes = json.dumps(message).encode(ENCODING)
    sock.send(message_bytes)
