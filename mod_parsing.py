from random import randint
import sqlite3
import requests
from telegram import ReplyKeyboardMarkup

reply_keyboard = [['/fruit'], ['/parsing'], ['/quiz']]
main_buttons = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)

async def parsing(update, context):
    await update.message.reply_text('Прямо СЕЙЧАС ведётся разработка!'
        )
    context.user_data['parsing'] = 1
    context.user_data['latest_mode'] = main_buttons