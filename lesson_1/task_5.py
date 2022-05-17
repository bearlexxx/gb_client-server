"""
Написать код, который выполняет пинг веб-ресурсов yandex.ru, youtube.com и преобразовывает результат из байтовового
типа данных в строковый без ошибок для любой кодировки операционной системы
"""


import platform
import subprocess
import chardet


def func_ping(domain):
    print(f'Ping: {domain}')
    param = '-n' if platform.system().lower() == 'windows' else '-c'
    args = ['ping', param, '4', domain]
    ping = subprocess.Popen(args, stdout=subprocess.PIPE)
    for line in ping.stdout:
        result = chardet.detect(line)
        line = line.decode(result['encoding']).encode('utf-8')
        print(line.decode('utf-8'), end='')


domain_list = ['yandex.ru', 'youtube.com']
for domain in domain_list:
    func_ping(domain)
