"""
3. Задание на закрепление знаний по модулю yaml.
 Написать скрипт, автоматизирующий сохранение данных
 в файле YAML-формата.
Для этого:

Подготовить данные для записи в виде словаря, в котором
первому ключу соответствует список, второму — целое число,
третьему — вложенный словарь, где значение каждого ключа —
это целое число с юникод-символом, отсутствующим в кодировке
ASCII(например, €);

Реализовать сохранение данных в файл формата YAML — например,
в файл file.yaml. При этом обеспечить стилизацию файла с помощью
параметра default_flow_style, а также установить возможность работы
с юникодом: allow_unicode = True;

Реализовать считывание данных из созданного файла и проверить,
совпадают ли они с исходными.
"""

import yaml


data = {'list_key': ['value1', 'value2', 'value3', 'value4', 'value5'],
        'int_key': 100,
        'dict_key':
            {'price1': '50\u20ac',
             'price2': '150\u20ac',
             'price3': '300\u20ac'}
        }


def write_to_yaml_and_read(py_data):

    with open('file.yaml', 'w', encoding='utf-8') as f:
        yaml.dump(py_data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)

    with open("file.yaml", 'r', encoding='utf-8') as f:
        data_from_yaml = yaml.load(f, Loader=yaml.SafeLoader)
    return data_from_yaml


def equality_pydata_yaml(py_data, yaml):
    print(f'Исходные данные: {py_data}\n'
          f'Данные из файла YAML-формата: {yaml}\n'
          f'Совпадают ли данные из файла YAML-формата с исходными: {py_data == yaml}')


equality_pydata_yaml(data, write_to_yaml_and_read(data))
# Вывод:
# Исходные данные: {'list_key': ['value1', 'value2', 'value3', 'value4', 'value5'], 'int_key': 100, 'dict_key': {'price1': '50€', 'price2': '150€', 'price3': '300€'}}
# Данные из файла YAML-формата: {'list_key': ['value1', 'value2', 'value3', 'value4', 'value5'], 'int_key': 100, 'dict_key': {'price1': '50€', 'price2': '150€', 'price3': '300€'}}
# Совпадают ли данные из файла YAML-формата с исходными: True
