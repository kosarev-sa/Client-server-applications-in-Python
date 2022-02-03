# Клиентская программа
import argparse
import sys
import json
import time
from socket import socket, AF_INET, SOCK_STREAM
from logging import getLogger

from globals.variables import ACTION, PRESENCE, TIME, USER, ACCOUNT_NAME, RESPONSE, ERROR, \
    DEFAULT_IP_ADDRESS, DEFAULT_PORT, MESSAGE, SENDER, MESSAGE_TEXT
from globals.utils import get_message, send_message
from log_config import client_log_config
from log_decors import log_dec


log = getLogger('client')


@log_dec
def message_from_server(msg):
    # Обработчик сообщений других пользователей, поступающих с сервера
    if ACTION in msg and msg[ACTION] == MESSAGE and SENDER in msg and MESSAGE_TEXT in msg:
        print(f'Получено сообщение от пользователя {msg[SENDER]}:\n{msg[MESSAGE_TEXT]}')
        log.info(f'Получено сообщение от пользователя {msg[SENDER]}:\n{msg[MESSAGE_TEXT]}')
    else:
        log.error(f'Некорректное сообщение с сервера: {msg}')


@log_dec
def create_msg(sock, account_name='Guest'):
    # Функция запрашивает пользовательский ввод сообщения и возвращает словарь с данными сообщения
    # Завершает работу при вводе комманды exit

    msg = input('Введите сообщение для отправки или "exit" для завершения работы: ')
    if msg == 'x':
        sock.close()
        log.info('Завершение работы по команде пользователя')
        print('Спасибо за использование нашего сервиса!')
        sys.exit(0)
    msg_dct = {
        ACTION: MESSAGE,
        TIME: time.time(),
        ACCOUNT_NAME: account_name,
        MESSAGE_TEXT: msg
    }
    log.debug(f'Подготовлены данные для сообщения: {msg_dct}')
    return msg_dct


@log_dec
def create_presence_msg(account_name='Guest'):
    # Функция генерирует сообщение о присутствии клиента
    # {'action': 'presence', 'time': 1642973242.1169634, 'user': {'account_name': 'Guest'}}
    user_presence_msg = {ACTION: PRESENCE,
                         TIME: time.time(),
                         USER:
                             {ACCOUNT_NAME: account_name}
                         }
    return user_presence_msg


@log_dec
def server_response_validator(msg):
    # Функция интерпретирует ответ сервера
    if RESPONSE in msg:
        if msg[RESPONSE] == 200:
            log.info('Клиент соединился с сервером. Подключение успешно')
            return '200 : OK'
        log.error('Клиент не подключен серверу')
        return f'400 : {msg[ERROR]}'
    log.error('Клиент не подключен серверу')
    raise ValueError


@log_dec
def arg_parser():
    # Парсер аргументов коммандной строки
    parser = argparse.ArgumentParser()
    parser.add_argument('addr', default=DEFAULT_IP_ADDRESS, nargs='?')
    parser.add_argument('port', default=DEFAULT_PORT, type=int, nargs='?')
    parser.add_argument('-m', '--mode', default='listen', nargs='?')
    parser.add_argument('-n', '--name', default='guest', nargs='?')
    namespace = parser.parse_args(sys.argv[1:])

    client_mode = namespace.mode
    client_name = namespace.name

    # Пробуем загрузить параметры командной строки (например, client.py 192.168.0.7 8079)
    # Если нет параметров, то задаём значения по умоланию
    try:
        server_address = namespace.addr
        server_port = namespace.port
        if not (server_port > 1023 or server_port < 65535):
            raise ValueError
    except IndexError:
        log.warning('server_address = DEFAULT_IP_ADDRESS, server_port = DEFAULT_PORT')
        server_address = DEFAULT_IP_ADDRESS
        server_port = DEFAULT_PORT
    except ValueError:
        # print('Номер порта - число от 1024 до 65535.')
        log.error('exit(1). Номер порта - число от 1024 до 65535')
        sys.exit(1)

    # Проверим допустим ли выбранный режим работы клиента
    if client_mode not in ('listen', 'send'):
        log.critical(f'Недопустимый режим работы {client_mode}, допустимые режимы: listen , send')
        sys.exit(1)

    return server_address, server_port, client_mode, client_name


def main_func():
    server_address, server_port, client_mode, client_name = arg_parser()

    try:
        s = socket(AF_INET, SOCK_STREAM)   # Создает сокет TCP (AF_INET — сетевой, SOCK_STREAM — потоковый)
        s.connect((server_address, server_port))

        msg_to_server = create_presence_msg()
        send_message(s, msg_to_server)  # Отправляет на сервер сообщение о присутствии клиента

        server_answer = server_response_validator(get_message(s))
        # print(server_answer)    # Код ответа сервера (200/400)
        log.info(f'Ответ сервера: "{server_answer}"')

    except (ValueError, json.JSONDecodeError):
        # print('Не удалось декодировать сообщение сервера.')
        log.error('Не удалось декодировать сообщение сервера')
    except ConnectionRefusedError:
        log.critical(f'Нет соединения с сервером {server_address}:{server_port}, отвергнут запрос на подключение')
        sys.exit(1)
    else:
        # Если соединение с сервером установлено корректно, начинается обмен с ним, согласно установленному режиму
        # Основной цикл прогрммы:
        if client_mode == 'send':
            print(f'Клиент {client_name}. Режим работы - отправка сообщений.')
        else:
            print(f'Клиент {client_name}. Режим работы - приём сообщений.')
        while True:
            # Режим работы - отправка сообщений
            if client_mode == 'send':
                try:
                    send_message(s, create_msg(s))
                except (ConnectionResetError, ConnectionError, ConnectionAbortedError):
                    log.error(f'Соединение с сервером {server_address} было потеряно')
                    sys.exit(1)

            # Режим работы - приём сообщений:
            if client_mode == 'listen':
                try:
                    message_from_server(get_message(s))
                except (ConnectionResetError, ConnectionError, ConnectionAbortedError):
                    log.error(f'Соединение с сервером {server_address} было потеряно')
                    sys.exit(1)


if __name__ == '__main__':
    main_func()
