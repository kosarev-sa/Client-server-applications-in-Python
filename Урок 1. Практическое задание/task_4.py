"""
Задание 4.

Преобразовать слова «разработка», «администрирование», «protocol»,
«standard» из строкового представления в байтовое и выполнить
обратное преобразование (используя методы encode и decode).

Подсказки:
--- используйте списки и циклы, не дублируйте функции
"""

a = 'разработка'
b = 'администрирование'
c = 'protocol'
d = 'standard'

vars_lst = [a, b, c, d]

# vars_lst = list(map(lambda x: x.encode('utf-8'), vars_lst))
for inx, item in enumerate(vars_lst):
    vars_lst[inx] = item.encode('utf-8')
    print(vars_lst[inx])

# Вывод
# b'\xd1\x80\xd0\xb0\xd0\xb7\xd1\x80\xd0\xb0\xd0\xb1\xd0\xbe\xd1\x82\xd0\xba\xd0\xb0'
# b'\xd0\xb0\xd0\xb4\xd0\xbc\xd0\xb8\xd0\xbd\xd0\xb8\xd1\x81\xd1\x82\xd1\x80\xd0\xb8\xd1\x80\xd0\xbe\xd0\xb2\xd0\xb0\xd0\xbd\xd0\xb8\xd0\xb5'
# b'protocol'
# b'standard'


# vars_lst = list(map(lambda x: x.decode('utf-8'), vars_lst))
for inx, item in enumerate(vars_lst):
    vars_lst[inx] = item.decode('utf-8')
    print(vars_lst[inx])

# Вывод
# разработка
# администрирование
# protocol
# standard
