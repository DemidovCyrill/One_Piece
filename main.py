from telegram.ext import CommandHandler
import logging
import requests
from telegram.ext import ConversationHandler
from random import choice, randint
from telegram.ext import Application, MessageHandler, filters
from telegram import ReplyKeyboardMarkup
BOT_TOKEN = '6048853518:AAFE1tEkAVFrJHw8YE8Rw3IYxuZmXo9fCyw'
#здесь описание индекса, на котором пользователь остановился в разделе фрект но порядку
number_fruit_in_order = 0
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG)
logger = logging.getLogger(__name__)
basa = requests.get('https://tools.aimylogic.com/api/googlesheet2json?sheet=Лист1&id=1-OMbqWih_VlXwhKJt_hOPEqD1-CH3zNsYh13Kc05nls').json()

#далее описываются статические клавиатуры
reply_keyboard = [['/fruit'], ['/parsing'], ['/quiz']]
main_buttons = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)

frut_keyboard = [['/random_fruit'], ['/fruit_line_in_order'], ['/help']]
frut_buttons = ReplyKeyboardMarkup(frut_keyboard, one_time_keyboard=True)

frut_random_keyboard = [['/previous', '/help', '/next_fruit']]
frut_random_keyboard = ReplyKeyboardMarkup(frut_random_keyboard, one_time_keyboard=True)

echo_data = ['Простите, но я не понимаю что вы говорите...', 'Надо же, не знал что это есть в мире One Piece!',
             'Если это есть в One Piece, то королём пиратов станет Усопп!',
             'Это точно есть в One Piece? Пойду пересмотрю арку энис лобби...',
             'Хммм... Возможно я упустил это в арке Алабаста, пойду пересмотрю',
             'Я помню что-то похожее в арке страны Вано, пойду пересмотрю...']


async def users_text(update, context):
    u_text = update.message.text
    #if 'но Ми' in u_text or 'но ми' in u_text:
    await update.message.reply_text(choice(echo_data), reply_markup=main_buttons)
    #

async def help(update, context):
    await update.message.reply_text('''
Здравствуйте, я бот-инциклопедя по One Piece! 

Здесь вы можете:
/fruit - узнать про любой фрукт;
/parsing - задать интересующие вопросы (нет);
/quiz - сыграть со мной в наинтерснейшую викторину (нет);

На этом пока что всё, сейчас ведётся активная разработка!
''', reply_markup=main_buttons)

async def fruit(update, context):
    global number_fruit_in_order
    number_fruit_in_order = 0
    await update.message.reply_text('''
    Отлично! Вы выбрали режим фруктов!
    
здесь вы можете найти:
случайный фрукт
по порядку

Пока на этом всё! приходите чуть позже, добавится ещё функционал, я обещаю!''', reply_markup=frut_buttons)

async def random_fruit(update, context):
    i = randint(0, 61)
    await update.message.reply_text(basa[i]['name'])
    await update.message.reply_text(basa[i]['line'])
    await update.message.reply_text(basa[i]['image'], reply_markup=frut_buttons)


async def next_fruit(update, context):
    global number_fruit_in_order
    number_fruit_in_order += 1
    try:
        x = basa[number_fruit_in_order]['name']
    except Exception:
        number_fruit_in_order = 0
        x = basa[number_fruit_in_order]['name']
    await update.message.reply_text(x)
    await update.message.reply_text(basa[number_fruit_in_order]['line'])
    await update.message.reply_text(basa[number_fruit_in_order]['image'], reply_markup=frut_random_keyboard)
async def previous(update, context):
    global number_fruit_in_order
    number_fruit_in_order -= 1
    try:
        x = basa[number_fruit_in_order]['name']
    except Exception:
        number_fruit_in_order = 0
        x = basa[number_fruit_in_order]['name']
    await update.message.reply_text(x)
    await update.message.reply_text(basa[number_fruit_in_order]['line'])
    await update.message.reply_text(basa[number_fruit_in_order]['image'], reply_markup=frut_random_keyboard)
async def fruit_line_in_order(update, context):
    global number_fruit_in_order
    try:
        x = basa[number_fruit_in_order]['name']
    except Exception:
        number_fruit_in_order = 0
        x = basa[number_fruit_in_order]['name']
    await update.message.reply_text(x)
    await update.message.reply_text(basa[number_fruit_in_order]['line'])
    await update.message.reply_text(basa[number_fruit_in_order]['image'], reply_markup=frut_random_keyboard)
async def fruit_statistics(update, context):
    await update.message.reply_text("fruit_statistics", reply_markup=main_buttons)


'''async def fruit(update, context):
    await update.message.reply_text('same text', reply_markup=markup)'''

async def parsing(update, context):
    await update.message.reply_text('''Пока закрыто...

Выберите то, что работает.''', reply_markup=main_buttons)


async def quiz(update, context):
    await update.message.reply_text('''Пока закрыто...

Выберите то, что работает.''', reply_markup=main_buttons)



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
