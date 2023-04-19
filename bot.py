import logging
import sqlite3
from random import choice, shuffle


import requests
from telegram import ReplyKeyboardMarkup
from telegram.ext import Application, MessageHandler, filters
from telegram.ext import CommandHandler

from mod_fruit import fruit, fruit_statistics, fruit_line_in_order
from mod_fruit import previous, next_fruit, random_fruit, check_in_data

from mod_quiz import quiz, rename, start_quiz, quiz_statistic, quiz_questions

from mod_parsing import parsing, parsing_character, parsing_character_request, \
    keyboard_of_random_buttons, parsing_place_request, parsing_place

#from bot_token import BOT_TOKEN
BOT_TOKEN = '6048853518:AAFE1tEkAVFrJHw8YE8Rw3IYxuZmXo9fCyw'


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
reply_keyboard = [['Фрукты'], ['Поиск'], ['Викторина']]
main_buttons = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)

fruit_keyboard = [['Случайный фрукт'], ['Фрукты по порядку'], ['Статистика'], ['Назад']]
fruit_buttons = ReplyKeyboardMarkup(fruit_keyboard, one_time_keyboard=True)

fruit_random_keyboard = [['←', 'Назад', '→']]
fruit_random_keyboard = ReplyKeyboardMarkup(fruit_random_keyboard, one_time_keyboard=True)

start_keyboard = [['Начать!'], ['Переименоваться'], ['Статистика'], ['Назад']]
start_keyboard = ReplyKeyboardMarkup(start_keyboard, one_time_keyboard=True)


''' В этой переменной хранится значения последней вызываемой клавиатуры у пользователя
будет складываться ощущение, что он находится в отдельном режиме '''



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

    if context.user_data == {}:
        context.user_data['latest_mode'] = main_buttons
    if update.message.text == 'Фрукты':
        await fruit(update, context)
        return
    if update.message.text == 'Поиск':
        await parsing(update, context)
        context.user_data['parsing_active'] = 1
        return
    if update.message.text == 'Викторина':
        await quiz(update, context)
        return
    if 'fruit_active' in context.user_data:
        if update.message.text == 'Случайный фрукт':
            await random_fruit(update, context)
            return
        if update.message.text == 'Фрукты по порядку':
            context.user_data.clear()
            await fruit_line_in_order(update, context)
            return
        if update.message.text == 'Статистика':
            await fruit_statistics(update, context)
            return
        if update.message.text == 'Назад':
            await help(update, context)
            return
        flag, index = check_in_data(update.message.text)
        if flag:
            id_user = int(list(filter(lambda x: x[:3] == 'id=', str(update).split()))[-1][3:-1])

            C.execute(f'select f_{index} from orders where token={id_user}')

            value = int(C.fetchall()[0][0])
            print(value)
            C.execute(f'''Update orders set f_{index} = {value + 1} where token = {id_user}''')
            BASE.commit()

            open("./tmp.gif", "wb").write(requests.get(fruits_db[index]['image']).content)
            await update.message.reply_photo(photo="./tmp.gif", caption=fruits_db[index]['name'],
                                             reply_markup=main_buttons)
            await update.message.reply_text(fruits_db[index]['line'], reply_markup=fruit_buttons)

            context.user_data['latest_mode'] = fruit_buttons
            return
        await update.message.reply_text('Такого фрукта нет, попробуйте ещё раз или выберите'
                                        ' из предложенных кнопок!', reply_markup=fruit_buttons)
        context.user_data['latest_mode'] = fruit_buttons
        return
    if 'number_fruit_in_order' in context.user_data:
        if update.message.text == '←':
            await previous(update, context)
            return
        if update.message.text == '→':
            await next_fruit(update, context)
            return
        if update.message.text == 'Назад':
            await fruit(update, context)
            context.user_data.clear()
            context.user_data['fruit_active'] = 1
            return
    if 'quiz_name' in context.user_data:
        id_user = int(list(filter(lambda x: x[:3] == 'id=', str(update).split()))[-1][3:-1])
        C.execute(f'''Update quiz_table set name = '{update.message.text}' where token = {id_user}''')
        BASE.commit()

        await update.message.reply_text(
            f'{update.message.text} - Отличное имя! Я его запомню. Если имя всё-таки имя не подходит, нажмите rename. '
            f'А теперь приступим к викторине! Нажмите Начать!', reply_markup=start_keyboard)

        context.user_data.clear()
        context.user_data['latest_mode'] = start_keyboard
        context.user_data['quiz'] = 0
        return
    #Это Режим викторины
    if 'quiz' in context.user_data:
        if update.message.text == 'Назад':
            await help(update, context)
            return
        if update.message.text == 'Начать!':
            print('started')
            await start_quiz(update, context)
            return
        if update.message.text == 'Переименоваться':
            await rename(update, context)
            return
        if update.message.text == 'Статистика':
            await quiz_statistic(update, context)
            return
    if 'quiz_active' in context.user_data:
        await quiz_questions(update, context)
        return
    if 'parsing_active' in context.user_data:
        if 'character_active' in context.user_data:
            await parsing_character_request(update, context)
            return
        if 'place_active' in context.user_data:
            await parsing_place_request(update, context)
            return
        if update.message.text == 'Персонаж':
            await parsing_character(update, context)
            context.user_data['character_active'] = 1
            return
        if update.message.text == 'Место':
            await parsing_place(update, context)
            context.user_data['place_active'] = 1
            return
        if update.message.text == 'случайный':
            await help(update, context)
            return
        if update.message.text == 'Другие случайные':
            await keyboard_of_random_buttons(update, context)
            return
        if update.message.text == 'Назад':
            context.user_data.clear()
            await help(update, context)
            return

    await update.message.reply_text(choice(echo_data), reply_markup=context.user_data['latest_mode'])


async def help(update, context):

    """ Функция приветствия с полизоватилем, а также
    эта функция работает как главный экран режимов """

    context.user_data.clear()
    context.user_data['latest_mode'] = start_keyboard

    await update.message.reply_text(
        'Здравствуйте, я бот-инциклопедя по One Piece!\n'
        '\n'
        '/fruit - узнать про любой фрукт;\n'
        '/parsing - задать интересующие вопросы (нет);\n'
        '/quiz - сыграть со мной в наинтерснейшую викторину (+-);\n'
        '\n'
        'На этом пока что всё, сейчас ведётся активная разработка!', reply_markup=main_buttons)

    context.user_data['latest_mode'] = main_buttons


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
    application.add_handler(CommandHandler('parsing_character', parsing_character))
    application.add_handler(CommandHandler('quiz_statistic', quiz_statistic))
    application.add_handler(CommandHandler('rename', rename))

    text_handler = MessageHandler(filters.TEXT, users_text)

    application.add_handler(text_handler)
    application.run_polling()


# Запускаем функцию main() в случае запуска скрипта.
if __name__ == '__main__':
    main()