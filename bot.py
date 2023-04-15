import logging
import sqlite3
from random import choice, shuffle

from parser import Parser

import requests
from telegram import ReplyKeyboardMarkup
from telegram.ext import Application, MessageHandler, filters
from telegram.ext import CommandHandler

from mod_fruit import fruit, fruit_statistics, fruit_line_in_order
from mod_fruit import previous, next_fruit, random_fruit, check_in_data

from mod_quiz import quiz, rename, start_quiz, quiz_statistic

from mod_parsing import parsing, parsing_character

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
reply_keyboard = [['/fruit'], ['/parsing'], ['/quiz']]
main_buttons = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)

fruit_keyboard = [['/random_fruit'], ['/fruit_line_in_order'], ['/fruit_statistics'], ['/help']]
fruit_buttons = ReplyKeyboardMarkup(fruit_keyboard, one_time_keyboard=True)

fruit_random_keyboard = [['/previous', '/help', '/next_fruit']]
fruit_random_keyboard = ReplyKeyboardMarkup(fruit_random_keyboard, one_time_keyboard=True)

start_keyboard = [['/start_quiz'], ['/rename'], ['/quiz_statistic'], ['/help']]
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

    if 'fruit_active' in context.user_data:
        flag, index = check_in_data(update.message.text)
        if flag:
            id_user = int(list(filter(lambda x: x[:3] == 'id=', str(update).split()))[-1][3:-1])

            C.execute(f'select f_{index} from orders where token={id_user}')

            value = int(C.fetchall()[0][0])
            print(value)
            C.execute(f'''Update orders set f_{index} = {value + 1} where token = {id_user}''')
            BASE.commit()

            await update.message.reply_text(fruits_db[index]['name'])
            await update.message.reply_text(fruits_db[index]['line'])
            await update.message.reply_text(fruits_db[index]['image'], reply_markup=fruit_buttons)

            context.user_data['latest_mode'] = fruit_buttons
            return
        await update.message.reply_text('Такого фрукта нет, попробуйте ещё раз или выберите'
                                        ' из предложенных кнопок!', reply_markup=fruit_buttons)
        context.user_data['latest_mode'] = fruit_buttons
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
        return
    #Это Режим викторины
    if 'quiz_active' in context.user_data:
        # Получаем номер вопроса
        num = context.user_data['quiz_active']
        # Проверяем совподение с верным
        if update.message.text == quiz_db[num]['answer']:
            # Сообщаем, что всё верно и начисляем баллы
            context.user_data['score'] += quiz_db[num]['exp']
            await update.message.reply_text(choice(['Да, верно!', 'Обсалютно верно!',
                                                    'За этот ответ вы заслуживаете баллы!',
                                                    'Как вам это удаётся?! Начисляю баллы!']))
        else:
            # Сообщаем верный ответ
            await update.message.reply_text(quiz_db[num]['link'])

        # Далее выводим новый вопрос с ответоми на клавиатуре и увеличиваем номер вопроса
        context.user_data['quiz_active'] += 1
        num += 1
        if num == 31:
            id_user = int(list(filter(lambda x: x[:3] == 'id=', str(update).split()))[-1][3:-1])

            C.execute(f'select record from quiz_table where token={id_user}')

            last_record = int(C.fetchall()[0][0])

            if context.user_data['score'] >= last_record:
                C.execute(f'''Update quiz_table set record = '{context.user_data['score']}' where token = {id_user}''')
                BASE.commit()
                await update.message.reply_text(f'Поздравляю, это ваш новый рекорд!\n'
                                                f'В прошлый раз вы набрали {last_record},'
                                                f"а в этот целых {context.user_data['score']}!!!\n"
                                                , reply_markup=main_buttons)
                await quiz_statistic(update, context)
                context.user_data['latest_mode'] = main_buttons
                return
            await update.message.reply_text('Результаты не плохие, но это не новый рекорд!\n'
                                            f'В прошлый раз вы набрали {last_record},'
                                            f"а в этот целых {context.user_data['score']}!!!\n"
                                            , reply_markup=main_buttons)
            await quiz_statistic(update, context)
            context.user_data.clear()
            context.user_data['latest_mode'] = main_buttons

        answers = quiz_db[num]['incorrect'].split()
        answers.append(quiz_db[num]['answer'])
        shuffle(answers)
        keyboard = ReplyKeyboardMarkup([answers, ['/help']], one_time_keyboard=True)

        await update.message.reply_text(f'{num + 1}-й вопрос: \n \n' + quiz_db[num]['question'], reply_markup=keyboard)

        context.user_data['latest_mode'] = main_buttons
        return
    if 'parsing_character' in context.user_data:
        await update.message.reply_text('Подождите секундочку...')
        q = Parser().search_character_by_name(request=update.message.text)
        text = f'Имя: {q.name}\n\n'\
               f'Возраст: {q.age}\n\n'\
               f'День рождения - {q.birth_date}\n\n'\
               f'Должность: {q.occupations }\n\n'\
               f'Первое появление: {q.first_appearance}\n\n'\
               f'Место проживания: {q.residences}\n\n'\
               f'Членские организации: {q.affiliations}\n\n'
        # await update.message.reply_text(f'Имя: {q.name}\n\n'
        #                                 f'Возраст: {q.age}\n\n'
        #                                 f'День рождения - {q.birth_date}\n\n'
        #                                 f'Должность: {q.occupations }\n\n'
        #                                 f'Первое появление: {q.first_appearance}\n\n'
        #                                 f'Место проживания: {q.residences}\n\n'
        #                                 f'Членские организации: {q.affiliations}\n\n', reply_markup=main_buttons)
        #await update.message.photo(q.images)
        #for image in q.images:
        #    open("./tmp.jpg", "wb").write(image)
        #    await update.message.reply_photo(photo="./tmp.jpg")
        try:
            open("./tmp.jpg", "wb").write(q.images[0])
            await update.message.reply_photo(photo="./tmp.jpg", caption=text, reply_markup=main_buttons)
        except IndexError:
            await update.message.reply_text(text, reply_markup=main_buttons)
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