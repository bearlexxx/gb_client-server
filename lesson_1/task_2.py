"""
Каждое из слов «class», «function», «method» записать в байтовом типе. Сделать это необходимо
в автоматическом, а не ручном режиме, с помощью добавления литеры b к текстовому значению,
(т.е. ни в коем случае не используя методы encode, decode или функцию bytes) и определить тип,
содержимое и длину соответствующих переменных
"""


def func_word(word):
    word_b = eval(f'b\'{word}\'')
    print(f'Value: {word_b}\n Type: {type(word_b)}\n Lenght: {len(word_b)}')


words = ['class', 'function', 'method']
for word in words:
    func_word(word)
