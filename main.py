from telegram.ext import CommandHandler
import logging
import requests
import sqlite3
from telegram.ext import ConversationHandler
from random import choice, randint
from telegram.ext import Application, MessageHandler, filters
from telegram import ReplyKeyboardMarkup
BOT_TOKEN = '6048853518:AAFE1tEkAVFrJHw8YE8Rw3IYxuZmXo9fCyw'
#здесь описание индекса, на котором пользователь остановился в разделе "фрукт но порядку"
number_fruit_in_order = 0
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG)
logger = logging.getLogger(__name__)
basa = requests.get('https://tools.aimylogic.com/api/googlesheet2json?sheet=Лист1&id=1-OMbqWih_VlXwhKJt_hOPEqD1-CH3zNsYh13Kc05nls').json()

#далее описываются статические клавиатуры
reply_keyboard = [['/fruit'], ['/parsing'], ['/quiz']]
main_buttons = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)

frut_keyboard = [['/random_fruit'], ['/fruit_line_in_order'], ['/fruit_statistics'], ['/help']]
frut_buttons = ReplyKeyboardMarkup(frut_keyboard, one_time_keyboard=True)

frut_random_keyboard = [['/previous', '/help', '/next_fruit']]
frut_random_keyboard = ReplyKeyboardMarkup(frut_random_keyboard, one_time_keyboard=True)

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
    #u_text = update.message.text
    #if 'но Ми' in u_text or 'но ми' in u_text:
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
/quiz - сыграть со мной в наинтерснейшую викторину (нет);

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
    global number_fruit_in_order
    # Обнуляем счётчик режима фруктов по порядку
    number_fruit_in_order = 0
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
    global number_fruit_in_order
    number_fruit_in_order = (number_fruit_in_order + 1) % (len(basa))
    try:
        x = basa[number_fruit_in_order]['name']
    except Exception:
        number_fruit_in_order = 0
        x = basa[number_fruit_in_order]['name']
    id_user = int(list(filter(lambda x: x[:3] == 'id=', str(update).split()))[-1][3:-1])
    C.execute(f"select f_{number_fruit_in_order} from orders where token={id_user}")
    znach = int(C.fetchall()[0][0])
    print(znach)
    C.execute(f"""Update orders set f_{number_fruit_in_order} = {znach + 1} where token = {id_user}""")
    BASE.commit()
    await update.message.reply_text(x)
    await update.message.reply_text(basa[number_fruit_in_order]['line'])
    await update.message.reply_text(basa[number_fruit_in_order]['image'], reply_markup=frut_random_keyboard)
    global latest_mode
    latest_mode = frut_random_keyboard
async def previous(update, context):
    global number_fruit_in_order
    number_fruit_in_order = (number_fruit_in_order - 1) % (len(basa))
    try:
        x = basa[number_fruit_in_order]['name']
    except Exception:
        number_fruit_in_order = 0
        x = basa[number_fruit_in_order]['name']
    id_user = int(list(filter(lambda x: x[:3] == 'id=', str(update).split()))[-1][3:-1])
    C.execute(f"select f_{number_fruit_in_order} from orders where token={id_user}")
    znach = int(C.fetchall()[0][0])
    print(znach)
    C.execute(f"""Update orders set f_{number_fruit_in_order} = {znach + 1} where token = {id_user}""")
    BASE.commit()
    await update.message.reply_text(x)
    await update.message.reply_text(basa[number_fruit_in_order]['line'])
    await update.message.reply_text(basa[number_fruit_in_order]['image'], reply_markup=frut_random_keyboard)
    global latest_mode
    latest_mode = frut_random_keyboard
async def fruit_line_in_order(update, context):
    global number_fruit_in_order
    try:
        x = basa[number_fruit_in_order]['name']
    except Exception:
        number_fruit_in_order = 0
        x = basa[number_fruit_in_order]['name']
    id_user = int(list(filter(lambda x: x[:3] == 'id=', str(update).split()))[-1][3:-1])
    C.execute(f"select f_{number_fruit_in_order} from orders where token={id_user}")
    znach = int(C.fetchall()[0][0])
    print(znach)
    C.execute(f"""Update orders set f_{number_fruit_in_order} = {znach + 1} where token = {id_user}""")
    BASE.commit()
    await update.message.reply_text(x)
    await update.message.reply_text(basa[number_fruit_in_order]['line'])
    await update.message.reply_text(basa[number_fruit_in_order]['image'], reply_markup=frut_random_keyboard)
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


'''async def fruit(update, context):
    await update.message.reply_text('same text', reply_markup=markup)'''

async def parsing(update, context):
    await update.message.reply_text('''Пока закрыто...

Выберите то, что работает.''', reply_markup=main_buttons)
    global latest_mode
    latest_mode = main_buttons


async def quiz(update, context):
    await update.message.reply_text('''Пока закрыто...

Выберите то, что работает.''', reply_markup=main_buttons)
    global latest_mode
    latest_mode = main_buttons



conv_handler = ConversationHandler(
    [CommandHandler('start', help)],
    fallbacks=[CommandHandler('stop', help)],
    states={
        # Функция читает ответ на первый вопрос и задаёт второй.
        'fruits_mod': [MessageHandler(filters.TEXT & ~filters.COMMAND, fruit)],
        'main': [MessageHandler(filters.TEXT & ~filters.COMMAND, help)],
        'fruit_line_in_order': [MessageHandler(filters.TEXT & ~filters.COMMAND, fruit_line_in_order)],
        # Функция читает ответ на второй вопрос и завершает диалог.
        'parsing_mod': [MessageHandler(filters.TEXT & ~filters.COMMAND, parsing)]
    },
    # Точка прерывания диалога. В данном случае — команда /stop.
    #fallbacks=[CommandHandler('stop', stop)]
)
#application.add_handler(conv_handler)

def main():
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
    text_handler = MessageHandler(filters.TEXT, users_text)
    application.add_handler(text_handler)
    application.run_polling()


# Запускаем функцию main() в случае запуска скрипта.
if __name__ == '__main__':
    main()
