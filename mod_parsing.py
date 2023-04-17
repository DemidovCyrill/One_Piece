from random import randint
import sqlite3
import requests
from parser import Parser
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



#----------------------------------------------------
async def parsing_character_request(update, context):
    await update.message.reply_text('Подождите секундочку...')
    q = Parser().search_character_by_name(request=update.message.text)
    text = f'Имя: {q.name}\n\n' \
           f'Возраст: {q.age}\n\n' \
           f'День рождения - {q.birth_date}\n\n' \
           f'Должность: {q.occupations}\n\n' \
           f'Первое появление: {q.first_appearance}\n\n' \
           f'Место проживания: {q.residences}\n\n' \
           f'Членские организации: {q.affiliations}\n\n'
    try:
        open("./tmp.jpg", "wb").write(q.images[0])
        await update.message.reply_photo(photo="./tmp.jpg", caption=text, reply_markup=main_buttons)
    except IndexError:
        await update.message.reply_text(text, reply_markup=main_buttons)