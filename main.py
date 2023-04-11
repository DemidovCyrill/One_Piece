from telegram.ext import CommandHandler
import logging
import requests
import sqlite3
from telegram.ext import ConversationHandler
from random import choice, randint
from telegram.ext import Application, MessageHandler, filters
from telegram import ReplyKeyboardMarkup
BOT_TOKEN = '6048853518:AAFE1tEkAVFrJHw8YE8Rw3IYxuZmXo9fCyw'
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG)
logger = logging.getLogger(__name__)
basa = requests.get('https://tools.aimylogic.com/api/googlesheet2json?sheet=Лист1&id=1-OMbqWih_VlXwhKJt_hOPEqD1-CH3zNsYh13Kc05nls').json()
basa_quiz = requests.get('https://tools.aimylogic.com/api/googlesheet2json?sheet=Лист2&id=1-OMbqWih_VlXwhKJt_hOPEqD1-CH3zNsYh13Kc05nls').json()

print(basa_quiz)
#далее описываются статические клавиатуры
reply_keyboard = [['/fruit'], ['/parsing'], ['/quiz']]
main_buttons = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)

frut_keyboard = [['/random_fruit'], ['/fruit_line_in_order'], ['/fruit_statistics'], ['/help']]
frut_buttons = ReplyKeyboardMarkup(frut_keyboard, one_time_keyboard=True)

frut_random_keyboard = [['/previous', '/help', '/next_fruit']]
frut_random_keyboard = ReplyKeyboardMarkup(frut_random_keyboard, one_time_keyboard=True)

start_keyboard = [['/start_quiz'], ['/rename']]
start_keyboard = ReplyKeyboardMarkup(start_keyboard, one_time_keyboard=True)

# В этой переменной хранится значения последней вызываемой клавиатуры
# у пользователя будет складываться ощущение, что он находится
# в отдельном режиме
latest_mode = main_buttons

# загрузка базы данных
BASE = sqlite3.connect("clients.db")
C = BASE.cursor()
# Если база данных фруктов (гугл таблца) была дополнена
# то не нужно вручную в программе всё менять
# сдесь поисходит дополнение столбцов
str_execute = ''
for i in range(len(basa)):
    str_execute = str_execute + ', f_' + str(i) + ' INT'
C.execute("""CREATE TABLE IF NOT EXISTS orders(
   token INT,
   record TEXT""" + str_execute + ');')
BASE.commit()

# Ответы на незапланированные запросы пользователя
echo_data = ['Простите, но я не понимаю что вы говорите...', 'Надо же, не знал что это есть в мире One Piece!',
             'Если это есть в One Piece, то королём пиратов станет Усопп!',
             'Это точно есть в One Piece? Пойду пересмотрю арку энис лобби...',
             'Хммм... Возможно я упустил это в арке Алабаста, пойду пересмотрю',
             'Я помню что-то похожее в арке страны Вано, пойду пересмотрю...']


async def users_text(update, context):
    """Функция, которая отвечает на все незапланированные запросы пользователя
    Она также может быть вызвана в любое время режима, не повлияв на него, ведь
    вконце мы возврещаем набор кнопок latest_mode, который хранит последний вызов клавиатуры"""
    global latest_mode
    if 'quiz_name' in context.user_data:
        id_user = int(list(filter(lambda x: x[:3] == 'id=', str(update).split()))[-1][3:-1])
        C.execute(f"""Update quiz_table set name = '{update.message.text}' where token = {id_user}""")
        BASE.commit()
        global start_keyboard
        await update.message.reply_text(f'''{update.message.text} - Отличное имя! Я его запомню.
Если имя всё-таки имя не подходит, нажмите rename.
А теперь приступим к викторине!
Нажмите Начать!''', reply_markup=start_keyboard)
        latest_mode = start_keyboard
        context.user_data.clear()
        return
    await update.message.reply_text(choice(echo_data), reply_markup=latest_mode)
    #

async def help(update, context):
    #берём айди пользователя
    #id_user = int(list(filter(lambda x: x[:3] == 'id=', str(update).split()))[-1][3:-1])
    #C.execute(f"select * from orders where token={id_user}")
    #print(C.fetchall())
    '''Функция приветствия с полизоватилем, а также
    эта функция работает как главный экран режимов'''
    await update.message.reply_text('''
Здравствуйте, я бот-инциклопедя по One Piece! 

Здесь вы можете:
/fruit - узнать про любой фрукт;
/parsing - задать интересующие вопросы (нет);
/quiz - сыграть со мной в наинтерснейшую викторину (+-);

На этом пока что всё, сейчас ведётся активная разработка!
''', reply_markup=main_buttons)
    global latest_mode
    latest_mode = main_buttons

async def fruit(update, context):
    """Эта функция работает как главный экран режима фруктов"""
    # берём айди пользователя и если он новый, то просто заносим его в БД
    id_user = int(list(filter(lambda x: x[:3] == 'id=', str(update).split()))[-1][3:-1])
    C.execute(f"select * from orders where token={id_user}")
    if C.fetchall() == []:
        cursor = BASE.execute('select * from orders')
        names = list(map(lambda x: x[0], cursor.description))
        C.execute(f"""INSERT INTO orders({', '.join(names)})
           VALUES('{id_user}'{', 0' * (len(basa) + 1)});""")
        BASE.commit()
        context.user_data['number_fruit_in_order'] = 0
    await update.message.reply_text('''
    Отлично! Вы выбрали режим фруктов!
    
Здесь вы можете найти:
    Случайный фрукт
    По порядку
    Статистику

Пока на этом всё! приходите чуть позже, добавится ещё функционал, я обещаю!''', reply_markup=frut_buttons)
    global latest_mode
    latest_mode = frut_buttons

async def random_fruit(update, context):
    i = randint(1, len(basa) - 1)
    id_user = int(list(filter(lambda x: x[:3] == 'id=', str(update).split()))[-1][3:-1])
    C.execute(f"select f_{i} from orders where token={id_user}")
    znach = int(C.fetchall()[0][0])
    print(znach)
    C.execute(f"""Update orders set f_{i} = {znach + 1} where token = {id_user}""")
    BASE.commit()
    await update.message.reply_text(basa[i]['name'])
    await update.message.reply_text(basa[i]['line'])
    await update.message.reply_text(basa[i]['image'], reply_markup=frut_buttons)
    global latest_mode
    latest_mode = frut_buttons


async def next_fruit(update, context):
    context.user_data['number_fruit_in_order'] = (context.user_data['number_fruit_in_order'] + 1) % (len(basa))
    try:
        x = basa[context.user_data['number_fruit_in_order']]['name']
    except Exception:
        context.user_data['number_fruit_in_order'] = 0
        x = basa[context.user_data['number_fruit_in_order']]['name']
    id_user = int(list(filter(lambda x: x[:3] == 'id=', str(update).split()))[-1][3:-1])
    C.execute(f"select f_{context.user_data['number_fruit_in_order']} from orders where token={id_user}")
    znach = int(C.fetchall()[0][0])
    print(znach)
    C.execute(f"""Update orders set f_{context.user_data['number_fruit_in_order']} = {znach + 1} where token = {id_user}""")
    BASE.commit()
    await update.message.reply_text(x)
    await update.message.reply_text(basa[context.user_data['number_fruit_in_order']]['line'])
    await update.message.reply_text(basa[context.user_data['number_fruit_in_order']]['image'], reply_markup=frut_random_keyboard)
    global latest_mode
    latest_mode = frut_random_keyboard
async def previous(update, context):
    context.user_data['number_fruit_in_order'] = (context.user_data['number_fruit_in_order'] - 1) % (len(basa))
    try:
        x = basa[context.user_data['number_fruit_in_order']]['name']
    except Exception:
        context.user_data['number_fruit_in_order'] = 0
        x = basa[context.user_data['number_fruit_in_order']]['name']
    id_user = int(list(filter(lambda x: x[:3] == 'id=', str(update).split()))[-1][3:-1])
    C.execute(f"select f_{context.user_data['number_fruit_in_order']} from orders where token={id_user}")
    znach = int(C.fetchall()[0][0])
    print(znach)
    C.execute(f"""Update orders set f_{context.user_data['number_fruit_in_order']} = {znach + 1} where token = {id_user}""")
    BASE.commit()
    await update.message.reply_text(x)
    await update.message.reply_text(basa[context.user_data['number_fruit_in_order']]['line'])
    await update.message.reply_text(basa[context.user_data['number_fruit_in_order']]['image'], reply_markup=frut_random_keyboard)
    global latest_mode
    latest_mode = frut_random_keyboard
async def fruit_line_in_order(update, context):
    try:
        x = basa[context.user_data['number_fruit_in_order']]['name']
    except Exception:
        context.user_data['number_fruit_in_order'] = 0
        x = basa[context.user_data['number_fruit_in_order']]['name']
    id_user = int(list(filter(lambda x: x[:3] == 'id=', str(update).split()))[-1][3:-1])
    C.execute(f"select f_{context.user_data['number_fruit_in_order']} from orders where token={id_user}")
    znach = int(C.fetchall()[0][0])
    C.execute(f"""Update orders set f_{context.user_data['number_fruit_in_order']} = {znach + 1} where token = {id_user}""")
    BASE.commit()
    await update.message.reply_text(x)
    await update.message.reply_text(basa[context.user_data['number_fruit_in_order']]['line'])
    await update.message.reply_text(basa[context.user_data['number_fruit_in_order']]['image'], reply_markup=frut_random_keyboard)
    global latest_mode
    latest_mode = frut_random_keyboard
async def fruit_statistics(update, context):
    id_user = int(list(filter(lambda x: x[:3] == 'id=', str(update).split()))[-1][3:-1])
    C.execute(f"select * from orders where token={id_user}")
    m = list(C.fetchall()[0][2:])
    print(m)
    first = max(m)
    ind_first = m.index(first)
    m[ind_first] = 0
    second = max(m)
    ind_second = m.index(second)
    m[ind_second] = 0
    third = max(m)
    ind_third = m.index(third)
    m[ind_third] = 0
    fourth = max(m)
    ind_fourth = m.index(fourth)
    m[ind_fourth] = 0
    fifth = max(m)
    ind_fifth = m.index(fifth)
    m[ind_fifth] = 0
    sixth = max(m)
    ind_sixth = m.index(sixth)
    m[ind_sixth] = 0
    seventh = max(m)
    ind_seventh = m.index(seventh)
    m[ind_seventh] = 0
    eighth = max(m)
    ind_eighth = m.index(eighth)
    m[ind_eighth] = 0
    ninth = max(m)
    ind_ninth = m.index(ninth)
    m[ind_ninth] = 0
    tenth = max(m)
    ind_tenth = m.index(tenth)
    m[ind_tenth] = 0
    await update.message.reply_text(f'''
Твои самые часто попадающиеся Дьявольские фрукты:
  1-е место - {basa[ind_first]['name']} ({first} раз)
  2-е место - {basa[ind_second]['name']} ({second} раз)
  3-е место - {basa[ind_third]['name']} ({third} раз)
  4-е место - {basa[ind_fourth]['name']} ({fourth} раз)
  5-е место - {basa[ind_fifth]['name']} ({fifth} раз)
  6-е место - {basa[ind_sixth]['name']} ({sixth} раз)
  7-е место - {basa[ind_seventh]['name']} ({seventh} раз)
  8-е место - {basa[ind_eighth]['name']} ({eighth} раз)
  9-е место - {basa[ind_ninth]['name']} ({ninth} раз)
  10-е место - {basa[ind_tenth]['name']} ({tenth} раз)
    ''', reply_markup=frut_buttons)
    global latest_mode
    latest_mode = frut_buttons

async def parsing(update, context):
    await update.message.reply_text('''Пока закрыто...

Выберите то, что работает.''', reply_markup=main_buttons)
    global latest_mode
    latest_mode = main_buttons


async def quiz(update, context):
    id_user = int(list(filter(lambda x: x[:3] == 'id=', str(update).split()))[-1][3:-1])
    C.execute(f"select * from quiz_table where token={id_user}")
    if C.fetchall() == []:
        cursor = BASE.execute('select * from quiz_table')
        names = list(map(lambda x: x[0], cursor.description))
        C.execute(f"""INSERT INTO quiz_table({', '.join(names)})
                   VALUES('{id_user}', 'name', 0, 0);""")
        BASE.commit()
        await update.message.reply_text('''
О, замечательно, хотите поиграть в викторину по моему любимому сериалу? Ну смотрите, каждый следующий вопрос будет всё сложнее!
Есть три уровня сложности:
Первый - даже не смотрящий сериала ответит на большинство вопросов;
Второй - только для фанатов, которые смотрели этот шедевр;
Третий - для тех кто живёт в мире One Piece, или просто у кого отличная память!

Только вот одна загвостка, я не знаю как к вам обращаться!

ВВЕДИТЕ ваше ИМЯ, которое будет отображаться у других пользователей.
Если вы ошибётесь, то ничего страшного, его можно будет поменять!
        ''')
        context.user_data['quiz_name'] = 1
        return
    global start_keyboard
    C.execute(f"select name from quiz_table where token={id_user}")
    user_name = C.fetchall()[0][0]
    await update.message.reply_text(f'''
О, замечательно, хотите ещё раз сыграть в викторину по моему любимому сериалу? Ну как вы помните, каждый следующий вопрос будет всё сложнее!

Если вам надоело имя "{user_name}", то нажмите rename, только помните, у остальных пользователей оно тоже меняется!

Если вы уже готовы начать, то нажмите Начать!
''', reply_markup=start_keyboard)
    global latest_mode
    latest_mode = start_keyboard


async def rename(update, context):
    context.user_data['quiz_name'] = 1
    await update.message.reply_text('Хорошо, переназавите себя так, будто пишите имя на листовке с наградами за йонко, где ваша фотография и награда 5 000 000 000 Белли!')

async def start_quiz(update, context):
    if 'quiz_active' not in context.user_data:
        context.user_data['quiz_active'] = 0
    else:
        context.user_data['quiz_active'] += 1
    num = context.user_data['quiz_active']
    keyboard = ReplyKeyboardMarkup([['/start_quiz']], one_time_keyboard=True)
    await update.message.reply_text(basa_quiz[num]['question'], reply_markup=keyboard)
    global latest_mode
    latest_mode = keyboard


def main():
    # application.add_handler(conv_handler)
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("help", help))
    application.add_handler(CommandHandler("quiz", quiz))
    application.add_handler(CommandHandler("fruit", fruit))
    application.add_handler(CommandHandler("parsing", parsing))
    application.add_handler(CommandHandler("start", help))
    application.add_handler(CommandHandler("fruit_statistics", fruit_statistics))
    application.add_handler(CommandHandler("fruit_line_in_order", fruit_line_in_order))
    application.add_handler(CommandHandler("previous", previous))
    application.add_handler(CommandHandler("next_fruit", next_fruit))
    application.add_handler(CommandHandler("random_fruit", random_fruit))
    application.add_handler(CommandHandler("start_quiz", start_quiz))
    application.add_handler(CommandHandler("rename", rename))
    text_handler = MessageHandler(filters.TEXT, users_text)
    application.add_handler(text_handler)
    application.run_polling()


# Запускаем функцию main() в случае запуска скрипта.
if __name__ == '__main__':
    main()
