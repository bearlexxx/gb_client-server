from subprocess import Popen, CREATE_NEW_CONSOLE


P_LIST = []
clients_count = 2

while True:
    USER = input(f'Запустить {clients_count * 2} клиентов (s) / Закрыть клиентов (x) / Выйти (q) ')

    if USER == 'q':
        break

    elif USER == 's':
        P_LIST.append(Popen('python server.py', creationflags=CREATE_NEW_CONSOLE))

        for _ in range(2):
            P_LIST.append(Popen('python client.py -m send', creationflags=CREATE_NEW_CONSOLE))
            P_LIST.append(Popen('python client.py -m listen', creationflags=CREATE_NEW_CONSOLE))

        print(f'Запущено {clients_count * 2} клиентов')
    elif USER == 'x':
        for p in P_LIST:
            p.kill()
        P_LIST.clear()