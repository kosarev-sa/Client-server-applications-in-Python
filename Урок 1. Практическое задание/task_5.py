"""
Задание 5.

Выполнить пинг веб-ресурсов yandex.ru, youtube.com и
преобразовать результаты из байтовового в строковый тип на кириллице.

Подсказки:
--- используйте модуль chardet, иначе задание не засчитается!!!
"""

import subprocess
import chardet

args = ['ping', 'yandex.ru']
subproc_ping = subprocess.Popen(args, stdout=subprocess.PIPE)
for line in subproc_ping.stdout:
    result = chardet.detect(line)
    line = line.decode(result['encoding']).encode('utf-8')
    print(f"{result['encoding']} >> utf-8:\n", line.decode('utf-8'))

# Вывод:
# ascii >> utf - 8:
#
# IBM866 >> utf - 8:
# Обмен
# пакетами
# с
# yandex.ru[77.88
# .55
# .77] с
# 32
# байтами
# данных:
#
# IBM866 >> utf - 8:
# Ответ
# от
# 77.88
# .55
# .77: число
# байт = 32
# время = 8
# мс
# TTL = 56
#
# IBM866 >> utf - 8:
# Ответ
# от
# 77.88
# .55
# .77: число
# байт = 32
# время = 8
# мс
# TTL = 56
#
# IBM866 >> utf - 8:
# Ответ
# от
# 77.88
# .55
# .77: число
# байт = 32
# время = 8
# мс
# TTL = 56
#
# IBM866 >> utf - 8:
# Ответ
# от
# 77.88
# .55
# .77: число
# байт = 32
# время = 13
# мс
# TTL = 56
#
# ascii >> utf - 8:
#
# IBM866 >> utf - 8:
# Статистика
# Ping
# для
# 77.88
# .55
# .77:
#
# IBM866 >> utf - 8:
# Пакетов: отправлено = 4, получено = 4, потеряно = 0
#
# IBM866 >> utf - 8:
# (0 % потерь)
#
# IBM866 >> utf - 8:
# Приблизительное
# время
# приема - передачи
# в
# мс:
#
# IBM866 >> utf - 8:
# Минимальное = 8
# мсек, Максимальное = 13
# мсек, Среднее = 9
# мсек


args = ['ping', 'youtube.com']
subproc_ping = subprocess.Popen(args, stdout=subprocess.PIPE)
for line in subproc_ping.stdout:
    result = chardet.detect(line)
    line = line.decode(result['encoding']).encode('utf-8')
    print(f"{result['encoding']} >> utf-8:\n", line.decode('utf-8'))

# Вывод:
# ascii >> utf - 8:
#
# IBM866 >> utf - 8:
# Обмен
# пакетами
# с
# youtube.com[74.125
# .205
# .91] с
# 32
# байтами
# данных:
#
# IBM866 >> utf - 8:
# Ответ
# от
# 74.125
# .205
# .91: число
# байт = 32
# время = 23
# мс
# TTL = 109
#
# IBM866 >> utf - 8:
# Ответ
# от
# 74.125
# .205
# .91: число
# байт = 32
# время = 24
# мс
# TTL = 108
#
# IBM866 >> utf - 8:
# Ответ
# от
# 74.125
# .205
# .91: число
# байт = 32
# время = 23
# мс
# TTL = 109
#
# IBM866 >> utf - 8:
# Ответ
# от
# 74.125
# .205
# .91: число
# байт = 32
# время = 23
# мс
# TTL = 108
#
# ascii >> utf - 8:
#
# IBM866 >> utf - 8:
# Статистика
# Ping
# для
# 74.125
# .205
# .91:
#
# IBM866 >> utf - 8:
# Пакетов: отправлено = 4, получено = 4, потеряно = 0
#
# IBM866 >> utf - 8:
# (0 % потерь)
#
# IBM866 >> utf - 8:
# Приблизительное
# время
# приема - передачи
# в
# мс:
#
# IBM866 >> utf - 8:
# Минимальное = 23
# мсек, Максимальное = 24
# мсек, Среднее = 23
# мсек
