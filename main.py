from telegram.ext import CommandHandler
import logging
import requests
from random import choice, randint
from telegram.ext import Application, MessageHandler, filters
from telegram import ReplyKeyboardMarkup
BOT_TOKEN = '6048853518:AAFE1tEkAVFrJHw8YE8Rw3IYxuZmXo9fCyw'
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG)
logger = logging.getLogger(__name__)
basa = requests.get('https://tools.aimylogic.com/api/googlesheet2json?sheet=Лист1&id=1-OMbqWih_VlXwhKJt_hOPEqD1-CH3zNsYh13Kc05nls').json()
reply_keyboard = [['/help', '/fruit'],
                  ['/parsing', '/quiz']]
markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False)
echo_data = ['Простите, но я не понимаю что вы говорите...', 'Надо же, не знал что это есть в мире One Piece!',
             'Если это есть в One Piece, то королём пиратов станет Усопп!',
             'Это точно есть в One Piece? Пойду пересмотрю арку энис лобби...',
             'Хммм... Возможно я упустил это в арке Алабаста, пойду пересмотрю',
             'Я помню что-то похожее в арке страны Вано, пойду пересмотрю...']


async def echo(update, context):
    await update.message.reply_text(choice(echo_data), reply_markup=markup)
    #update.message.text

async def help(update, context):
    await update.message.reply_text("help", reply_markup=markup)

async def fruit(update, context):
    i = randint(0, 59)
    await update.message.reply_text(basa[i]['name'])
    await update.message.reply_text(basa[i]['line'])
    await update.message.reply_text(basa[i]['image'], reply_markup=markup)

async def parsing(update, context):
    await update.message.reply_text("parsing", reply_markup=markup)


async def quiz(update, context):
    await update.message.reply_text("quiz", reply_markup=markup)


def main():
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("help", help))
    application.add_handler(CommandHandler("fruit", fruit))
    application.add_handler(CommandHandler("parsing", parsing))
    application.add_handler(CommandHandler("start", help))
    text_handler = MessageHandler(filters.TEXT, echo)
    application.add_handler(text_handler)
    application.run_polling()


# Запускаем функцию main() в случае запуска скрипта.
if __name__ == '__main__':
    main()
