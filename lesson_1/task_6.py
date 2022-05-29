"""
Создать текстовый файл test_file.txt, заполнить его тремя строками: «сетевое программирование»,
«сокет», «декоратор». Далее забыть о том, что мы сами только что создали этот файл и исходить из
того, что перед нами файл в неизвестной кодировке. Задача: открыть этот файл БЕЗ ОШИБОК вне
зависимости от того, в какой кодировке он был создан.
"""

import chardet

f_name = 'test_file.txt'
data_to_file = ['сетевое программирование', 'сокет', 'декоратор']

with open(f_name, 'w') as f:
    f.write(f'{data_to_file}\n')
f.close()

with open('test_file.txt', 'rb') as f:
    data = f.read()
encoding = chardet.detect(data)['encoding']
print(encoding)

with open('test_file.txt', 'r', encoding=encoding) as f:
    data = f.read()
print(data)
f.close()
