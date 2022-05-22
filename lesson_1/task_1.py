"""
Каждое из слов «разработка», «сокет», «декоратор» представить в строковом формате и
проверить тип и содержание соответствующих переменных. Затем с помощью
онлайн-конвертера преобразовать строковые представление в формат Unicode и также
проверить тип и содержимое переменных.
Конвертер: https://calcsbox.com/post/konverter-teksta-v-unikod.html
"""


def check_word(word_in, word_utf):
    print(f'Value: {word_in}\n Type: {type(word_in)}')
    print(f'Value: {word_utf}\n Type: {type(word_utf)}')
    print('*' * 20)


check_word('разработка', '\u0440\u0430\u0437\u0440\u0430\u0431\u043e\u0442\u043a\u0430')
check_word('сокет', '\u0441\u043e\u043a\u0435\u0442')
check_word('декоратор', '\u0434\u0435\u043a\u043e\u0440\u0430\u0442\u043e\u0440')
