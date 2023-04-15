from random import randint
import sqlite3
import requests
from telegram import ReplyKeyboardMarkup

reply_keyboard = [['/fruit'], ['/parsing'], ['/quiz']]
main_buttons = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)

parsing_keyboard = [['/parsing_character', 'Место'], ['случайный', 'Другие случайные'], ['/help']]
parsing_buttons = ReplyKeyboardMarkup(parsing_keyboard, one_time_keyboard=True)

async def parsing(update, context):
    await update.message.reply_text(
        'Выберите один из режимов, затем ввидите свой запрос!\n\n'
        'Сейчас работает только /parsing_character \n\n'
        'Прямо СЕЙЧАС ведётся разработка!',
        reply_markup=parsing_buttons)
    context.user_data['parsing'] = 1
    context.user_data['latest_mode'] = parsing_buttons

async def parsing_character(update, context):
    await update.message.reply_text('Введите имя персонажа из One Piece!')
    context.user_data['parsing_character'] = 1