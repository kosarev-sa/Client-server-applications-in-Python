# Клиентская программа

import sys
import json
from socket import socket, AF_INET, SOCK_STREAM
import time
from globals.variables import ACTION, PRESENCE, TIME, USER, ACCOUNT_NAME, RESPONSE, ERROR, \
    DEFAULT_IP_ADDRESS, DEFAULT_PORT
from globals.utils import get_message, send_message


def create_presence_msg(account_name='Guest'):
    # Функция генерирует сообщение о присутствии клиента
    # {'action': 'presence', 'time': 1642973242.1169634, 'user': {'account_name': 'Guest'}}
    user_presence_msg = {ACTION: PRESENCE,
                         TIME: time.time(),
                         USER:
                             {ACCOUNT_NAME: account_name}
                         }
    return user_presence_msg


def server_response_validator(msg):
    # Функция интерпретирует ответ сервера
    if RESPONSE in msg:
        if msg[RESPONSE] == 200:
            return '200 : OK'
        return f'400 : {msg[ERROR]}'
    raise ValueError


def main():
    # Пробуем загрузить параметры командной строки (например, client.py 192.168.0.7 8079)
    # Если нет параметров, то задаём значения по умоланию
    try:
        server_address = sys.argv[1]
        server_port = int(sys.argv[2])
        if not (server_port > 1023 or server_port < 65535):
            raise ValueError
    except IndexError:
        server_address = DEFAULT_IP_ADDRESS
        server_port = DEFAULT_PORT
    except ValueError:
        print('Номер порта - число от 1024 до 65535.')
        sys.exit(1)

    s = socket(AF_INET, SOCK_STREAM)   # Создает сокет TCP (AF_INET — сетевой, SOCK_STREAM — потоковый)
    s.connect((server_address, server_port))

    msg_to_server = create_presence_msg()
    send_message(s, msg_to_server)  # Отправляет на сервер сообщение о присутствии клиента
    try:
        server_answer = server_response_validator(get_message(s))
        print(server_answer)    # Код ответа сервера (200/400)
    except (ValueError, json.JSONDecodeError):
        print('Не удалось декодировать сообщение сервера.')


if __name__ == '__main__':
    main()
