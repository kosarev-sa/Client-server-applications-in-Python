"""
Задание 2.

Каждое из слов «class», «function», «method» записать в байтовом формате
без преобразования в последовательность кодов
не используя!!! методы encode и decode)
и определить тип, содержимое и длину соответствующих переменных.

Подсказки:
--- b'class' - используйте маркировку b''
--- используйте списки и циклы, не дублируйте функции
"""

a = b'class'
b = b'function'
c = b'method'

vars_lst = [a, b, c]
for val in vars_lst:
    print(val, type(val), len(val))

# Вывод
# b'class' <class 'bytes'> 5
# b'function' <class 'bytes'> 8
# b'method' <class 'bytes'> 6
