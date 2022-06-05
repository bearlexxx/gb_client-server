"""
Определить, какие из слов «attribute», «класс», «функция», «type» невозможно записать в
байтовом типе.
"""

words = ['attribute', 'класс', 'функция', 'type']

for word in words:
    try:
        word.encode('ascii')
    except UnicodeEncodeError:
        print(f'"{word}" невозможно записать в байтовом типе')
    else:
        print(f'"{word}" возможно записать в байтовом типе')
