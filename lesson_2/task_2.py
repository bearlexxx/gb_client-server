"""
2. Задание на закрепление знаний по модулю json. Есть файл orders
в формате JSON с информацией о заказах. Написать скрипт, автоматизирующий
его заполнение данными. Для этого:
Создать функцию write_order_to_json(), в которую передается
5 параметров — товар (item), количество (quantity), цена (price),
покупатель (buyer), дата (date). Функция должна предусматривать запись
данных в виде словаря в файл orders.json. При записи данных указать
величину отступа в 4 пробельных символа;
Проверить работу программы через вызов функции write_order_to_json()
с передачей в нее значений каждого параметра.
"""

import json
import pathlib
from datetime import datetime


def write_order_to_json(item, quantity, price, buyer, date):
    f_name = 'orders.json'

    path = pathlib.Path(f_name)
    if not path.is_file():
        orders_json = json.loads('{"orders": []}')
    else:
        with open(f_name, encoding='utf-8') as f:
            orders_json = json.load(f)

    new_order = {'item': item, 'quantity': quantity, 'price': price, 'buyer': buyer, 'date': str(date)}
    orders_json['orders'].append(new_order)

    with open(f_name, 'w', encoding='utf-8') as f:
        json.dump(orders_json, f, indent=4, ensure_ascii=False)


write_order_to_json('Мяч', 4, 4500, 'Алексей', datetime.now())
