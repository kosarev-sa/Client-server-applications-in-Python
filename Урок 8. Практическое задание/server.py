# Серверная программа

import sys
import json
import time
from socket import socket, AF_INET, SOCK_STREAM
from logging import getLogger
import argparse
from select import select

from globals.variables import ACTION, ACCOUNT_NAME, RESPONSE, MAX_CONNECTIONS, PRESENCE, TIME, USER, ERROR, \
    DEFAULT_PORT, MESSAGE_TEXT, MESSAGE, SENDER, RESPONSE_200, RESPONSE_400, DESTINATION, EXIT
from globals.utils import get_message, send_message
from log_config import server_log_config
from log_decors import LogDecCls

log = getLogger('server')


@LogDecCls()
def client_message_validator(msg, msg_lst, client, users_names, all_clients):
    # Если это сообщение о присутствии, принимает и отвечает, если успех
    # Валидатор проверяет корректность словаря, переданного сообщением клиента
    # (наличие [ACTION]==PRESENCE, [USER][ACCOUNT_NAME]=='Guest', TIME)
    if ACTION in msg and msg[ACTION] == PRESENCE and TIME in msg and USER in msg:
        # Если пользователь не зарегистрирован, регистрирует, иначе отправляет ответ и завершает соединение.
        if msg[USER][ACCOUNT_NAME] not in users_names.keys():
            log.info('Соединение с сервером клиента %s. Успешно' % msg[USER][ACCOUNT_NAME])
            users_names[msg[USER][ACCOUNT_NAME]] = client
            send_message(client, RESPONSE_200)
        else:
            response = RESPONSE_400
            response[ERROR] = 'Указанное имя пользователя занято.'
            send_message(client, response)
            all_clients.remove(client)
            client.close()
        return
    # Если это сообщение не о присутствии, то добавляет его в очередь сообщений. Ответ не требуется
    elif ACTION in msg and msg[ACTION] == MESSAGE and MESSAGE_TEXT in msg \
            and SENDER in msg and DESTINATION in msg and TIME in msg:
        msg_lst.append(msg)
        return
    # Если клиент выходит
    elif ACTION in msg and msg[ACTION] == EXIT and USER in msg:
        log.info('Соединение с сервером клиента %s разорвано' % msg[USER][ACCOUNT_NAME])
        all_clients.remove(users_names[msg[USER][ACCOUNT_NAME]])
        users_names[msg[USER][ACCOUNT_NAME]].close()
        del users_names[msg[USER][ACCOUNT_NAME]]
        return
    # Иначе 'Bad request'
    else:
        response = RESPONSE_400
        response[ERROR] = 'Некорректный запрос.'
        send_message(client, response)
        return


@LogDecCls()
def send_address_message(msg, users_names, w_socks):
    # Отправка сообщения определённому клиенту.
    # Принимает сообщение, список зарегистрированых пользователей и сокеты на запись (слушающие).
    # Ничего не возвращает.
    if msg[DESTINATION] in users_names and users_names[msg[DESTINATION]] in w_socks:
        send_message(users_names[msg[DESTINATION]], msg)
        log.info(f'Сообщение отправлено -> {msg[DESTINATION]} от: {msg[SENDER]}')
    elif msg[DESTINATION] in users_names and users_names[msg[DESTINATION]] not in w_socks:
        raise ConnectionError
    else:
        log.error(
            f'Пользователь {msg[DESTINATION]} не зарегистрирован на сервере, отправка сообщения невозможна')


@LogDecCls()
def arg_parser():
    # Парсер аргументов коммандной строки
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', default=DEFAULT_PORT, type=int, nargs='?')
    parser.add_argument('-a', default='', nargs='?')
    namespace = parser.parse_args(sys.argv[1:])

    # Пробуем загрузить параметры командной строки (например, server.py -p 8079 -a 192.168.0.7)
    # Если нет параметров, то задаём значения по умоланию

    # Порт:
    try:
        listen_port = namespace.p
        if not (listen_port > 1023 or listen_port < 65535):
            raise ValueError
    except IndexError:
        # print('Проверьте номер порта. Пример указания параметров командной строки:\n'
        #       '(-\'p\' номер порта -\'a\' адрес, который будет слушать сервер).\n'
        #       'Parameters: -\'p\' 8079 -\'a\' 192.168.0.7.')
        log.critical('exit(1). Проверьте номер порта. Пример: Parameters: -\'p\' 8079 -\'a\' 192.168.0.7')
        sys.exit(1)
    except ValueError:
        # print('Номер порта - число от 1024 до 65535.')
        log.critical('exit(1). Номер порта - число от 1024 до 65535')
        sys.exit(1)

    # IP-адрес:
    try:
        listen_address = namespace.a
    except IndexError:
        # print('Проверьте IP-адрес. Пример указания параметров командной строки:\n'
        #       '(-\'p\' номер порта -\'a\' адрес, который будет слушать сервер).\n'
        #       'Parameters: -\'p\' 8079 -\'a\' 192.168.0.7.')
        log.critical('exit(1). Проверьте IP-адрес. Пример: Parameters: -\'p\' 8079 -\'a\' 192.168.0.7')
        sys.exit(1)

    return listen_address, listen_port


def main_func():
    listen_address, listen_port = arg_parser()

    s = socket(AF_INET, SOCK_STREAM)  # Создает сокет TCP (AF_INET — сетевой, SOCK_STREAM — потоковый)
    s.bind((listen_address, listen_port))
    s.settimeout(0.5)

    # Список клиентов
    clients = []
    # Список (очередь) сообщений
    messages = []
    # Словарь имен пользователей и соответствующих им сокетов
    users_names = {}

    s.listen(MAX_CONNECTIONS)  # Переходит в режим ожидания запросов, одновременно обслуживает не более MAX_CONNECTIONS
    log.info(f'Готовность к соединению')

    # Основной цикл программы
    while True:
        # Ожидание подключения. Если таймаут вышел, ловит исключение
        try:
            client, client_address = s.accept()  # Принять запрос на соединение
        except OSError:
            pass
        else:
            log.info(f'Установлено соедение с {client_address}')
            clients.append(client)

        recv_lst = []
        send_lst = []
        err_lst = []

        # Проверяет на наличие ждущих клиентов
        try:
            if clients:
                recv_lst, send_lst, err_lst = select(clients, clients, [], 0)
        except OSError:
            pass

        # Сервер принимает данные. Если там есть сообщения, кладёт в словарь. Если ошибка, исключает клиента.
        if recv_lst:
            for r_client in recv_lst:
                try:
                    client_message_validator(get_message(r_client), messages, r_client, users_names, clients)
                except:
                    log.info(f'Клиент {r_client.getpeername()} отключился от сервера')
                    clients.remove(r_client)

        # Обрабатываем каждое сообщение, если они есть
        for msg in messages:
            try:
                send_address_message(msg, users_names, send_lst)
            except:
                log.info(f'Связь с клиентом {msg[DESTINATION]} потеряна')
                clients.remove(users_names[msg[DESTINATION]])
                del users_names[msg[DESTINATION]]
        messages.clear()


if __name__ == '__main__':
    main_func()
