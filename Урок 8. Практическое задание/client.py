# Клиентская программа

import argparse
import sys
import json
import time
from socket import socket, AF_INET, SOCK_STREAM
from logging import getLogger
import threading

from globals.variables import ACTION, PRESENCE, TIME, USER, ACCOUNT_NAME, RESPONSE, ERROR, \
    DEFAULT_IP_ADDRESS, DEFAULT_PORT, MESSAGE, SENDER, MESSAGE_TEXT, EXIT, DESTINATION
from globals.utils import get_message, send_message
from log_config import client_log_config
from log_decors import log_dec

log = getLogger('client')


@log_dec
def message_from_server(sock, selfusername):
    # Обработчик сообщений других пользователей, поступающих с сервера
    while True:
        try:
            msg = get_message(sock)
            if ACTION in msg and msg[ACTION] == MESSAGE and MESSAGE_TEXT in msg \
                    and SENDER in msg and DESTINATION in msg and msg[DESTINATION] == selfusername:
                print(f'\nCообщение от {msg[SENDER]}: {msg[MESSAGE_TEXT]}')
                log.info(f'Cообщение от {msg[SENDER]}: {msg[MESSAGE_TEXT]}')
            else:
                log.error(f'Некорректное сообщение с сервера: {msg}')
        except (OSError, ConnectionError, ConnectionAbortedError, ConnectionResetError, json.JSONDecodeError):
            log.critical(f'Потеряно соединение с сервером')
            break


@log_dec
def create_msg(sock, account_name='Guest'):
    # Функция запрашивает ввод получателя, ввод сообщения и возвращает словарь с данными сообщения
    # Завершает работу при вводе комманды exit

    to_user = input('Введите получателя сообщения: ')
    msg = input('Введите сообщение для отправки: ')
    msg_dct = {ACTION: MESSAGE,
               SENDER: account_name,
               DESTINATION: to_user,
               MESSAGE_TEXT: msg,
               TIME: time.time()
               }
    log.debug(f'Подготовлены данные для сообщения: {msg_dct}')
    try:
        send_message(sock, msg_dct)
        log.info(f'Отправлено сообщение -> {to_user}')
    except:
        log.critical('Потеряно соединение с сервером')
        sys.exit(1)


@log_dec
def user_interactive(sock, username):
    # Функция для получение команды от пользователя на отправку сообщений или завершение работы
    while True:
        print(username)
        aim = input('Введите команду ("msg" - ввод получателя->Enter->текст сообщения для отправки, '
                    'или "exit" - завершение работы):\n')
        if aim == 'msg':
            create_msg(sock, username)
        elif aim == 'exit':
            send_message(sock, create_exit_msg(username))
            log.info('Завершение работы по команде пользователя')
            print('Спасибо за использование нашего сервиса!')
            # Задержка для необходимого времени доставки сообщения о выходе
            time.sleep(1)
            break
        else:
            log.info('Неизвестная команда пользователя')
            print('Неизвестная команда, попробойте снова.')


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
def create_exit_msg(account_name):
    # Функция генерирует сообщение о выходе клиента
    user_exit_msg = {ACTION: EXIT,
                     TIME: time.time(),
                     USER:
                         {ACCOUNT_NAME: account_name}
                     }
    return user_exit_msg


@log_dec
def server_response_validator(msg):
    # Функция интерпретирует ответ сервера
    if RESPONSE in msg:
        if msg[RESPONSE] == 200:
            log.info('Клиент соединился с сервером. Подключение успешно')
            return '200 : OK'
        log.error('Клиент не подключен к серверу')
        return f'400 : {msg[ERROR]}'
    log.error('Клиент не подключен серверу')
    raise ValueError


@log_dec
def arg_parser():
    # Парсер аргументов коммандной строки
    parser = argparse.ArgumentParser()
    parser.add_argument('addr', default=DEFAULT_IP_ADDRESS, nargs='?')
    parser.add_argument('port', default=DEFAULT_PORT, type=int, nargs='?')
    parser.add_argument('-n', '--name', default='guest', nargs='?')
    namespace = parser.parse_args(sys.argv[1:])

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
    return server_address, server_port, client_name


def main_func():
    server_address, server_port, client_name = arg_parser()

    # Запрос имени пользователя, если ранее не задано
    if not client_name:
        client_name = input('Введите имя пользователя: ')

    try:
        s = socket(AF_INET, SOCK_STREAM)  # Создает сокет TCP (AF_INET — сетевой, SOCK_STREAM — потоковый)
        s.connect((server_address, server_port))

        msg_to_server = create_presence_msg(client_name)
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
        # Если соединение с сервером установлено корректно, запускаем потоки приёма и отправки сообщений.
        # Основной цикл прогрммы:

        # Поток приёма сообщний
        recv_thr = threading.Thread(target=message_from_server, args=(s, client_name))
        recv_thr.daemon = True
        recv_thr.start()

        # Поток отправки сообщений и взаимодействие с пользователем.
        send_thr = threading.Thread(target=user_interactive, args=(s, client_name))
        send_thr.daemon = True
        send_thr.start()

        log.debug('Открыты потоки приёма и отправки сообщений')

        # Справка: Если один из потоков завершён, значит или потеряно соединение или пользователь ввёл exit.
        # Поскольку все события обработываются в 'демонических' потоках, достаточно просто завершить основной цикл.
        while True:
            time.sleep(1)
            if recv_thr.is_alive() and send_thr.is_alive():
                continue
            break


if __name__ == '__main__':
    main_func()
