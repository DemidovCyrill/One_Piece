from random import shuffle, choice
import sqlite3
import requests
from telegram import ReplyKeyboardMarkup

fruits_db = requests.get(
    'https://tools.aimylogic.com/api/googlesheet2json?sheet=Лист1&id=1-OMbqWih_VlXwhKJt_hOPEqD1-CH3zNsYh13Kc05nls')\
    .json()

quiz_db = requests.get(
    'https://tools.aimylogic.com/api/googlesheet2json?sheet=Лист2&id=1-OMbqWih_VlXwhKJt_hOPEqD1-CH3zNsYh13Kc05nls')\
    .json()

BASE = sqlite3.connect('clients.db')
C = BASE.cursor()

''' далее описываются статические клавиатуры '''
start_keyboard = [['Начать!'], ['Переименоваться'], ['Статистика'], ['Назад']]
start_keyboard = ReplyKeyboardMarkup(start_keyboard, one_time_keyboard=True)

reply_keyboard = [['Фрукты'], ['Поиск'], ['Викторина']]
main_buttons = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)



''' В этой переменной хранится значения последней вызываемой клавиатуры у пользователя
будет складываться ощущение, что он находится в отдельном режиме '''



async def quiz(update, context):
    context.user_data['quiz'] = 0
    id_user = int(list(filter(lambda x: x[:3] == 'id=', str(update).split()))[-1][3:-1])
    C.execute(f'select * from quiz_table where token={id_user}')

    if not C.fetchall():
        cursor = BASE.execute('select * from quiz_table')
        names = list(map(lambda x: x[0], cursor.description))
        C.execute(f'''INSERT INTO quiz_table({', '.join(names)}) VALUES('{id_user}', 'name', 0, 0);''')
        BASE.commit()
        await update.message.reply_text(
            'О, замечательно, хотите поиграть в викторину по моему любимому сериалу? '
            'Ну смотрите, каждый следующий вопрос будет всё сложнее!\n'
            'Есть три уровня сложности:\n'
            'Первый - даже не смотрящий сериала ответит на большинство вопросов;\n'
            'Второй - только для фанатов, которые смотрели этот шедевр;\n'
            'Третий - для тех кто живёт в мире One Piece, или просто у кого отличная память!\n'
            '\n'
            'Только вот одна загвостка, я не знаю как к вам обращаться!\n'
            '\n'
            'ВВЕДИТЕ ваше ИМЯ, которое будет отображаться у других пользователей.\n'
            'Если вы ошибётесь, то ничего страшного, его можно будет поменять!\n')
        context.user_data['quiz_name'] = 1
        return

    C.execute(f'select name from quiz_table where token={id_user}')
    user_name = C.fetchall()[0][0]

    await update.message.reply_text(
        f'О, замечательно, хотите ещё раз сыграть в викторину по моему любимому сериалу? '
        f'Ну как вы помните, каждый следующий вопрос будет всё сложнее!\n'
        f'\n'
        f'Если вам надоело имя \'{user_name}\', '
        f'то нажмите rename, только помните, у остальных пользователей оно тоже меняется!\n'
        f'\n'
        f'Если вы уже готовы начать, то нажмите Начать!\n', reply_markup=start_keyboard)

    context.user_data['latest_mode'] = start_keyboard


async def rename(update, context):
    context.user_data['quiz_name'] = 1
    await update.message.reply_text(
        'Хорошо, переназавите себя так, будто пишите имя на листовке с наградами за йонко, '
        'где ваша фотография и награда 5 000 000 000 Белли!')


async def quiz_statistic(update, context):
    cursor = BASE.execute('select * from quiz_table')
    mas = []
    for i in cursor:
        mas.append(i)
        #await update.message.reply_text(f'{i}')
    mas = sorted(mas, key=lambda x: x[2] * (-1))
    text_statistic = 'Топ 3 лучших игроков:'
    for i in range(3):
        text_statistic += f'\n{i + 1}-е место: {mas[i][1]} - {mas[i][2]} балл!'
    await update.message.reply_text(text_statistic, reply_markup=start_keyboard)
    context.user_data['latest_mode'] = start_keyboard

async def start_quiz(update, context):
    if 'quiz_active' not in context.user_data:
        context.user_data['quiz_active'] = 0
        context.user_data['score'] = 0
    else:
        context.user_data['quiz_active'] += 1

    num = context.user_data['quiz_active']
    answers = quiz_db[num]['incorrect'].split()
    answers.append(quiz_db[num]['answer'])
    shuffle(answers)
    keyboard = ReplyKeyboardMarkup([answers, ['Выйти']], one_time_keyboard=True)

    await update.message.reply_text(f'{num + 1}-й вопрос: \n \n' + quiz_db[num]['question'], reply_markup=keyboard)

    context.user_data['latest_mode'] = keyboard

async def quiz_questions(update, context):
    # Получаем номер вопроса
    num = context.user_data['quiz_active']
    # Проверяем совподение с верным
    if update.message.text == 'Выйти':
        await quiz(update, context)
        return
    if update.message.text == quiz_db[num]['answer']:
        # Сообщаем, что всё верно и начисляем баллы
        context.user_data['score'] += quiz_db[num]['exp']
        await update.message.reply_text(choice(['Да, верно!', 'Абсолютно верно!',
                                                'За этот ответ вы заслуживаете баллы!',
                                                'Как вам это удаётся?! Начисляю баллы!']))
    else:
        # Сообщаем верный ответ
        await update.message.reply_text(quiz_db[num]['link'])

    # Далее выводим новый вопрос с ответоми на клавиатуре и увеличиваем номер вопроса
    context.user_data['quiz_active'] += 1
    num += 1
    if num == 32:
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
        context.user_data['quiz'] = 0
        context.user_data['latest_mode'] = main_buttons

    answers = quiz_db[num]['incorrect'].split()
    answers.append(quiz_db[num]['answer'])
    shuffle(answers)
    keyboard = ReplyKeyboardMarkup([answers, ['Выйти']], one_time_keyboard=True)

    await update.message.reply_text(f'{num + 1}-й вопрос: \n \n' + quiz_db[num]['question'], reply_markup=keyboard)

    context.user_data['latest_mode'] = main_buttons