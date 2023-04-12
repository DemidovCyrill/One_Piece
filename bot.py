import logging
import sqlite3
from random import choice, randint

import requests
from telegram import ReplyKeyboardMarkup
from telegram.ext import Application, MessageHandler, filters
from telegram.ext import CommandHandler

from bot_token import BOT_TOKEN


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG)
logger = logging.getLogger(__name__)


fruits_db = requests.get(
    'https://tools.aimylogic.com/api/googlesheet2json?sheet=Лист1&id=1-OMbqWih_VlXwhKJt_hOPEqD1-CH3zNsYh13Kc05nls')\
    .json()

quiz_db = requests.get(
    'https://tools.aimylogic.com/api/googlesheet2json?sheet=Лист2&id=1-OMbqWih_VlXwhKJt_hOPEqD1-CH3zNsYh13Kc05nls')\
    .json()

''' далее описываются статические клавиатуры '''
reply_keyboard = [['/fruit'], ['/parsing'], ['/quiz']]
main_buttons = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)

fruit_keyboard = [['/random_fruit'], ['/fruit_line_in_order'], ['/fruit_statistics'], ['/help']]
fruit_buttons = ReplyKeyboardMarkup(fruit_keyboard, one_time_keyboard=True)

fruit_random_keyboard = [['/previous', '/help', '/next_fruit']]
fruit_random_keyboard = ReplyKeyboardMarkup(fruit_random_keyboard, one_time_keyboard=True)

start_keyboard = [['/start_quiz'], ['/rename']]
start_keyboard = ReplyKeyboardMarkup(start_keyboard, one_time_keyboard=True)


''' В этой переменной хранится значения последней вызываемой клавиатуры у пользователя
будет складываться ощущение, что он находится в отдельном режиме '''

latest_mode = main_buttons


# загрузка базы данных
BASE = sqlite3.connect('clients.db')
C = BASE.cursor()


''' Если база данных фруктов (гугл таблца) была дополнена, то не нужно вручную
в программе всё менять здесь поисходит дополнение столбцов '''

str_execute = ''
for i in range(len(fruits_db)):
    str_execute = str_execute + ', f_' + str(i) + ' INT'

C.execute('''CREATE TABLE IF NOT EXISTS orders(token INT, record TEXT''' + str_execute + ');')

BASE.commit()


# Ответы на незапланированные запросы пользователя
echo_data = ['Простите, но я не понимаю что вы говорите...',
             'Надо же, не знал что это есть в мире One Piece!',
             'Если это есть в One Piece, то королём пиратов станет Усопп!',
             'Это точно есть в One Piece? Пойду пересмотрю арку энис лобби...',
             'Хммм... Возможно я упустил это в арке Алабаста, пойду пересмотрю',
             'Я помню что-то похожее в арке страны Вано, пойду пересмотрю...']


async def users_text(update, context):

    """ Функция, которая отвечает на все незапланированные запросы пользователя
    Она также может быть вызвана в любое время режима, не повлияв на него, ведь
    вконце мы возврещаем набор кнопок latest_mode, который хранит последний вызов клавиатуры """

    global latest_mode
    global start_keyboard

    if 'quiz_name' in context.user_data:
        id_user = int(list(filter(lambda x: x[:3] == 'id=', str(update).split()))[-1][3:-1])
        C.execute(f'''Update quiz_table set name = '{update.message.text}' where token = {id_user}''')
        BASE.commit()

        await update.message.reply_text(
            f'{update.message.text} - Отличное имя! Я его запомню. Если имя всё-таки имя не подходит, нажмите rename. '
            f'А теперь приступим к викторине! Нажмите Начать!', reply_markup=start_keyboard)

        latest_mode = start_keyboard
        context.user_data.clear()
        return

    await update.message.reply_text(choice(echo_data), reply_markup=latest_mode)


async def help(update, _context):

    """ Функция приветствия с полизоватилем, а также
    эта функция работает как главный экран режимов """

    global latest_mode

    await update.message.reply_text(
        'Здравствуйте, я бот-инциклопедя по One Piece!\n'
        '\n'
        '/fruit - узнать про любой фрукт;\n'
        '/parsing - задать интересующие вопросы (нет);\n'
        '/quiz - сыграть со мной в наинтерснейшую викторину (+-);\n'
        '\n'
        'На этом пока что всё, сейчас ведётся активная разработка!', reply_markup=main_buttons)

    latest_mode = main_buttons


async def fruit(update, context):

    """ Эта функция работает как главный экран режима фруктов """

    global latest_mode

    # берём айди пользователя и если он новый, то просто заносим его в БД
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
        'Пока на этом всё! приходите чуть позже, добавится ещё функционал, я обещаю!', reply_markup=fruit_buttons)

    latest_mode = fruit_buttons


async def random_fruit(update, _context):
    global latest_mode

    range_ = randint(1, len(fruits_db) - 1)
    id_user = int(list(filter(lambda x: x[:3] == 'id=', str(update).split()))[-1][3:-1])

    C.execute(f'select f_{range_} from orders where token={id_user}')

    value = int(C.fetchall()[0][0])
    print(value)
    C.execute(f'''Update orders set f_{range_} = {value + 1} where token = {id_user}''')
    BASE.commit()

    await update.message.reply_text(fruits_db[range_]['name'])
    await update.message.reply_text(fruits_db[range_]['line'])
    await update.message.reply_text(fruits_db[range_]['image'], reply_markup=fruit_buttons)

    latest_mode = fruit_buttons


async def next_fruit(update, context):
    global latest_mode

    context.user_data['number_fruit_in_order'] = (context.user_data['number_fruit_in_order'] + 1) % (len(fruits_db))

    try:
        x = fruits_db[context.user_data['number_fruit_in_order']]['name']
    except Exception as e:
        print(e)

        context.user_data['number_fruit_in_order'] = 0
        x = fruits_db[context.user_data['number_fruit_in_order']]['name']

    id_user = int(list(filter(lambda x: x[:3] == 'id=', str(update).split()))[-1][3:-1])
    C.execute(f'''select f_{context.user_data['number_fruit_in_order']} from orders where token={id_user}''')

    value = int(C.fetchall()[0][0])
    print(value)

    C.execute(
        f'''Update orders set f_{context.user_data['number_fruit_in_order']} = {value + 1} where token = {id_user}''')
    BASE.commit()

    await update.message.reply_text(x)
    await update.message.reply_text(fruits_db[context.user_data['number_fruit_in_order']]['line'])
    await update.message.reply_text(fruits_db[context.user_data['number_fruit_in_order']]['image'],
                                    reply_markup=fruit_random_keyboard)

    latest_mode = fruit_random_keyboard


async def previous(update, context):
    global latest_mode

    context.user_data['number_fruit_in_order'] = (context.user_data['number_fruit_in_order'] - 1) % (len(fruits_db))

    try:
        x = fruits_db[context.user_data['number_fruit_in_order']]['name']
    except Exception as e:
        print(e)

        context.user_data['number_fruit_in_order'] = 0
        x = fruits_db[context.user_data['number_fruit_in_order']]['name']

    id_user = int(list(filter(lambda x: x[:3] == 'id=', str(update).split()))[-1][3:-1])
    C.execute(f'''select f_{context.user_data['number_fruit_in_order']} from orders where token={id_user}''')

    value = int(C.fetchall()[0][0])
    print(value)

    C.execute(
        f'''Update orders set f_{context.user_data['number_fruit_in_order']} = {value + 1} where token = {id_user}''')

    BASE.commit()

    await update.message.reply_text(x)
    await update.message.reply_text(fruits_db[context.user_data['number_fruit_in_order']]['line'])
    await update.message.reply_text(fruits_db[context.user_data['number_fruit_in_order']]['image'],
                                    reply_markup=fruit_random_keyboard)

    latest_mode = fruit_random_keyboard


async def fruit_line_in_order(update, context):
    global latest_mode

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

    await update.message.reply_text(x)
    await update.message.reply_text(fruits_db[context.user_data['number_fruit_in_order']]['line'])
    await update.message.reply_text(fruits_db[context.user_data['number_fruit_in_order']]['image'],
                                    reply_markup=fruit_random_keyboard)

    latest_mode = fruit_random_keyboard


async def fruit_statistics(update, _context):
    global latest_mode

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

    latest_mode = fruit_buttons


async def parsing(update, _context):
    await update.message.reply_text('''Пока закрыто...

Выберите то, что работает.''', reply_markup=main_buttons)
    global latest_mode
    latest_mode = main_buttons


async def quiz(update, context):
    global start_keyboard
    global latest_mode

    id_user = int(list(filter(lambda x: x[:3] == 'id=', str(update).split()))[-1][3:-1])
    C.execute(f'select * from quiz_table where token={id_user}')

    if not C.fetchall():
        cursor = BASE.execute('select * from quiz_table')
        names = list(map(lambda x: x[0], cursor.description))
        C.execute(f'''INSERT INTO quiz_table({', '.join(names)}) VALUES('{id_user}', 'name', 0, 0);''')
        BASE.commit()
        await update.message.reply_text(
            'О, замечательно, хотите поиграть в викторину по моему любимому сериалу? '
            'Ну смотрите, каждый следующий вопрос будет всё сложнее!\n'
            'Есть три уровня сложности:\n'
            'Первый - даже не смотрящий сериала ответит на большинство вопросов;\n'
            'Второй - только для фанатов, которые смотрели этот шедевр;\n'
            'Третий - для тех кто живёт в мире One Piece, или просто у кого отличная память!\n'
            '\n'
            'Только вот одна загвостка, я не знаю как к вам обращаться!\n'
            '\n'
            'ВВЕДИТЕ ваше ИМЯ, которое будет отображаться у других пользователей.\n'
            'Если вы ошибётесь, то ничего страшного, его можно будет поменять!\n')
        context.user_data['quiz_name'] = 1
        return

    C.execute(f'select name from quiz_table where token={id_user}')
    user_name = C.fetchall()[0][0]

    await update.message.reply_text(
        f'О, замечательно, хотите ещё раз сыграть в викторину по моему любимому сериалу? '
        f'Ну как вы помните, каждый следующий вопрос будет всё сложнее!\n'
        f'\n'
        f'Если вам надоело имя \'{user_name}\', '
        f'то нажмите rename, только помните, у остальных пользователей оно тоже меняется!\n'
        f'\n'
        f'Если вы уже готовы начать, то нажмите Начать!\n', reply_markup=start_keyboard)

    latest_mode = start_keyboard


async def rename(update, context):
    context.user_data['quiz_name'] = 1
    await update.message.reply_text(
        'Хорошо, переназавите себя так, будто пишите имя на листовке с наградами за йонко, '
        'где ваша фотография и награда 5 000 000 000 Белли!')


async def start_quiz(update, context):
    global latest_mode

    if 'quiz_active' not in context.user_data:
        context.user_data['quiz_active'] = 0
    else:
        context.user_data['quiz_active'] += 1

    num = context.user_data['quiz_active']
    keyboard = ReplyKeyboardMarkup([['/start_quiz']], one_time_keyboard=True)

    await update.message.reply_text(quiz_db[num]['question'], reply_markup=keyboard)

    latest_mode = keyboard


def main():
    # application.add_handler(conv_handler)
    application = Application.builder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler('help', help))
    application.add_handler(CommandHandler('quiz', quiz))
    application.add_handler(CommandHandler('fruit', fruit))
    application.add_handler(CommandHandler('parsing', parsing))
    application.add_handler(CommandHandler('start', help))
    application.add_handler(CommandHandler('fruit_statistics', fruit_statistics))
    application.add_handler(CommandHandler('fruit_line_in_order', fruit_line_in_order))
    application.add_handler(CommandHandler('previous', previous))
    application.add_handler(CommandHandler('next_fruit', next_fruit))
    application.add_handler(CommandHandler('random_fruit', random_fruit))
    application.add_handler(CommandHandler('start_quiz', start_quiz))
    application.add_handler(CommandHandler('rename', rename))

    text_handler = MessageHandler(filters.TEXT, users_text)

    application.add_handler(text_handler)
    application.run_polling()


# Запускаем функцию main() в случае запуска скрипта.
if __name__ == '__main__':
    main()
