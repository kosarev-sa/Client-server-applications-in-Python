# Серверная программа

from socket import socket, AF_INET, SOCK_STREAM
import sys
import json
from globals.variables import ACTION, ACCOUNT_NAME, RESPONSE, MAX_CONNECTIONS, PRESENCE, TIME, USER, ERROR, DEFAULT_PORT
from globals.utils import get_message, send_message
from logging import getLogger
from log_config import server_log_config


log = getLogger('server')


def client_message_validator(msg):
    # Валидатор проверяет корректность словаря, переданного сообщением клиента
    # (наличие [ACTION]==PRESENCE, [USER][ACCOUNT_NAME]=='Guest', TIME)
    # возвращает словарь-ответ для клиента по результатам проверки сообщения
    if ACTION in msg and msg[ACTION] == PRESENCE and TIME in msg and USER in msg and msg[USER][ACCOUNT_NAME] == 'Guest':
        log.info('Соединение с сервером клиента %s. Успешно' % msg[USER][ACCOUNT_NAME])
        return {RESPONSE: 200}
    log.error('Некорректный запрос на соединение')
    return {RESPONSE: 400, ERROR: 'Bad Request'}


def main():
    # Пробуем загрузить параметры командной строки (например, server.py -p 8079 -a 192.168.0.7)
    # Если нет параметров, то задаём значения по умоланию

    # Порт:
    try:
        listen_port = int(sys.argv[sys.argv.index('-p') + 1]) if '-p' in sys.argv else DEFAULT_PORT
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
        listen_address = sys.argv[sys.argv.index('-a') + 1] if '-a' in sys.argv else ''
    except IndexError:
        # print('Проверьте IP-адрес. Пример указания параметров командной строки:\n'
        #       '(-\'p\' номер порта -\'a\' адрес, который будет слушать сервер).\n'
        #       'Parameters: -\'p\' 8079 -\'a\' 192.168.0.7.')
        log.critical('exit(1). Проверьте IP-адрес. Пример: Parameters: -\'p\' 8079 -\'a\' 192.168.0.7')
        sys.exit(1)

    s = socket(AF_INET, SOCK_STREAM)     # Создает сокет TCP (AF_INET — сетевой, SOCK_STREAM — потоковый)
    s.bind((listen_address, listen_port))

    s.listen(MAX_CONNECTIONS)   # Переходит в режим ожидания запросов, одновременно обслуживает не более MAX_CONNECTIONS

    log.info(f'Готовность к соединению')

    while True:
        client, address = s.accept()    # Принять запрос на соединение
        try:
            msg_from_client = get_message(client)

            # print(msg_from_client, address)     # Выводит декодированные данные принятого сообщения, IP и порт клиента
            # # {'action': 'presence', 'time': 1642973242.1169634, 'user': {'account_name': 'Guest'}} ('192.168.0.7', 54092)

            log.info(f'Принято сообщение от {address}, декодировано: {msg_from_client}')

            # Валидация сообщения
            response = client_message_validator(msg_from_client)

            # Отправка кода ответа сервера (200/400)
            send_message(client, response)
            client.close()

        except (ValueError, json.JSONDecodeError):
            # print('Некорретные данные сообщения от клиента.')
            log.error('Некорретные данные сообщения от клиента')
            client.close()


if __name__ == '__main__':
    main()
