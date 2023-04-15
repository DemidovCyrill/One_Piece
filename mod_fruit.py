from random import randint
import sqlite3
import requests
from telegram import ReplyKeyboardMarkup

fruits_db = requests.get(
    'https://tools.aimylogic.com/api/googlesheet2json?sheet=Лист1&id=1-OMbqWih_VlXwhKJt_hOPEqD1-CH3zNsYh13Kc05nls')\
    .json()

quiz_db = requests.get(
    'https://tools.aimylogic.com/api/googlesheet2json?sheet=Лист2&id=1-OMbqWih_VlXwhKJt_hOPEqD1-CH3zNsYh13Kc05nls')\
    .json()

BASE = sqlite3.connect('clients.db')
C = BASE.cursor()

''' далее описываются статические клавиатуры '''
reply_keyboard = [['Фрукты'], ['Поиск'], ['Викторина']]
main_buttons = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)

fruit_keyboard = [['Случайный фрукт'], ['Фрукты по порядку'], ['Статистика'], ['Назад']]
fruit_buttons = ReplyKeyboardMarkup(fruit_keyboard, one_time_keyboard=True)

fruit_random_keyboard = [['←', 'Назад', '→']]
fruit_random_keyboard = ReplyKeyboardMarkup(fruit_random_keyboard, one_time_keyboard=True)

start_keyboard = [['Начать'], ['Поменять имя'], ['Результаты']]
start_keyboard = ReplyKeyboardMarkup(start_keyboard, one_time_keyboard=True)


''' В этой переменной хранится значения последней вызываемой клавиатуры у пользователя
будет складываться ощущение, что он находится в отдельном режиме '''


def check_in_data(text):
    for ii in fruits_db:
        for i in text.split():
            if i.lower() in ii['entity']:
                return True, fruits_db.index(ii)
    return False, -1

async def fruit(update, context):

    """ Эта функция работает как главный экран режима фруктов """

    # берём айди пользователя и если он новый, то просто заносим его в БД

    context.user_data['fruit_active'] = True
    id_user = int(list(filter(lambda x: x[:3] == 'id=', str(update).split()))[-1][3:-1])
    C.execute(f'select * from orders where token={id_user}')

    if not C.fetchall():
        cursor = BASE.execute('select * from orders')
        names = list(map(lambda x: x[0], cursor.description))

        C.execute(f'''INSERT INTO orders({', '.join(names)})
           VALUES('{id_user}'{', 0' * (len(fruits_db) + 1)});''')

        BASE.commit()
        context.user_data['number_fruit_in_order'] = 0

    await update.message.reply_text(
        'Отлично! Вы выбрали режим фруктов!\n'
        '\n'
        'Здесь вы можете найти:\n'
        'Случайный фрукт\n'
        'По порядку\n'
        'Статистику\n'
        '\n'
        'Так же просто введите название фрукта, а я попытаюсь вам про него рассказать!\n'
        '\n'
        'Пока на этом всё! приходите чуть позже, добавится ещё функционал, я обещаю!', reply_markup=fruit_buttons)

    context.user_data['latest_mode'] = fruit_buttons


async def random_fruit(update, context):
    range_ = randint(1, len(fruits_db) - 1)
    id_user = int(list(filter(lambda x: x[:3] == 'id=', str(update).split()))[-1][3:-1])

    C.execute(f'select f_{range_} from orders where token={id_user}')

    value = int(C.fetchall()[0][0])
    print(value)
    C.execute(f'''Update orders set f_{range_} = {value + 1} where token = {id_user}''')
    BASE.commit()
    open("./tmp.png", "wb").write(requests.get(fruits_db[range_]['image']).content)
    await update.message.reply_photo(photo="./tmp.png", caption=fruits_db[range_]['name'], reply_markup=main_buttons)
    await update.message.reply_text(fruits_db[range_]['line'], reply_markup=fruit_buttons)

    context.user_data['latest_mode'] = fruit_buttons



async def fruit_line_in_order(update, context):
    try:
        x = fruits_db[context.user_data['number_fruit_in_order']]['name']
    except Exception as e:
        print(e)

        context.user_data['number_fruit_in_order'] = 0
        x = fruits_db[context.user_data['number_fruit_in_order']]['name']

    id_user = int(list(filter(lambda x: x[:3] == 'id=', str(update).split()))[-1][3:-1])
    C.execute(f'''select f_{context.user_data['number_fruit_in_order']} from orders where token={id_user}''')

    value = int(C.fetchall()[0][0])
    C.execute(
        f'''Update orders set f_{context.user_data['number_fruit_in_order']} = {value + 1} where token = {id_user}''')

    BASE.commit()

    range_ = context.user_data['number_fruit_in_order']
    open("./tmp.png", "wb").write(requests.get(fruits_db[range_]['image']).content)
    await update.message.reply_photo(photo="./tmp.png", caption=fruits_db[range_]['name'])
    await update.message.reply_text(fruits_db[range_]['line'], reply_markup=fruit_random_keyboard)

    context.user_data['latest_mode'] = fruit_random_keyboard


async def next_fruit(update, context):
    context.user_data['number_fruit_in_order'] = (context.user_data['number_fruit_in_order'] + 1) % len(fruits_db)
    await fruit_line_in_order(update, context)


async def previous(update, context):
    context.user_data['number_fruit_in_order'] = (context.user_data['number_fruit_in_order'] - 1) % len(fruits_db)
    await fruit_line_in_order(update, context)

async def fruit_statistics(update, context):
    id_user = int(list(filter(lambda x: x[:3] == 'id=', str(update).split()))[-1][3:-1])
    C.execute(f'select * from orders where token={id_user}')

    m = list(C.fetchall()[0][2:])

    print(m)

    counts = []
    for i in range(10):
        max_count = max(m)

        if not max_count:
            break

        ind_max = m.index(max_count)
        m[ind_max] = 0
        counts.append((max_count, ind_max))

    message = 'Твои самые часто попадающиеся Дьявольские фрукты:\n'
    for i, (count, index) in enumerate(counts):
        name = fruits_db[index]['name']
        message += f'{i + 1}-е место - {name} ({count} раз)\n'

    await update.message.reply_text(message, reply_markup=fruit_buttons)

    context.user_data['latest_mode'] = fruit_buttons
