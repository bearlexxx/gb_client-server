"""
Преобразовать слова «разработка», «администрирование», «protocol», «standard» из
строкового представления в байтовое и выполнить обратное преобразование (используя
методы encode и decode).
"""


def func_word(word):
    word_b = word.encode('utf-8')
    print(word_b)
    word_str = word_b.decode('utf-8')
    print(word_str)
    print('*' * 20)


words = ['разработка', 'администрирование', 'protocol', 'standard']

for word in words:
    func_word(word)
