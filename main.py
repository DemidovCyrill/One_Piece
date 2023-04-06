from telegram.ext import CommandHandler
import logging
from random import choice
from telegram.ext import Application, MessageHandler, filters
BOT_TOKEN = '6048853518:AAFE1tEkAVFrJHw8YE8Rw3IYxuZmXo9fCyw'
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG)
logger = logging.getLogger(__name__)
echo_data = ['Простите, но я не понимаю что вы говорите...', 'Надо же, не знал что это есть в мире One Piece!',
             'Если это есть в One Piece, то королём пиратов станет Усопп!',
             'Это точно есть в One Piece? Пойду пересмотрю арку энис лобби...',
             'Хммм... Возможно я упустил это в арке Алабаста, пойду пересмотрю',
             'Я помнб что-то похожее в арке страны Вано, пойду пересмотрю...']


async def echo(update, context):
    await update.message.reply_text(choice(echo_data))
    #update.message.text

async def help(update, context):
    await update.message.reply_text("help")

async def fruit(update, context):
    await update.message.reply_text('fruit')

async def parsing(update, context):
    await update.message.reply_text("parsing")


async def quiz(update, context):
    await update.message.reply_text("quiz")


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
