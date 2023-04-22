from random import randint
import objects
from parser import Parser
from telegram import ReplyKeyboardMarkup

prepared_words = ['Луффи', 'Эйс', 'Гол Д. Роджер',
                  'Нами', 'Зоро', 'Брук',
                  'Эльбаф', 'Реверс Маунтин', 'Остров Кактус',
                  'Страна Вано', 'Дзо', 'Скайпия', 'Зунеша',
                  'Пираты Сердца', 'Эмма', 'Соломенная шляпа',
                  'Дэн Дэн Муси', 'Морской Король', 'MADS', 'Рамбл Болл']


def parsing_buttons(context):
    prepared_words_interim = context.user_data['prepared_words_interim'] = prepared_words[:]
    parsing_keyboard = [['Персонаж', 'Место'],
                        [prepared_words_interim[randint(0, len(prepared_words_interim) - 1)], 'Другие случайные'],
                        ['Найти другой объект', 'Назад']]
    return ReplyKeyboardMarkup(parsing_keyboard, one_time_keyboard=True)


async def parsing(update, context):
    buttons = parsing_buttons(context)
    await update.message.reply_text(
        'Вижу вы любопытный?..  Хорошо! Я дам ответы на все ваши вопросы!\n'
        'Но сначала вам нужно их задать.\n'
        '\n'
        'Сейчас расскажу, как это делать:\n'
        '   Персонаж  – поиск по имени интересующей вас личности\n'
        '   Место  – поиск  локации или острова по названию\n'
        '   Случайный объект  – мною подготовленный термин, он ищется при нажатии.\n'
        '   Другие случайные  – нажав на эту кнопку, вы сможете выбрать другой Случайный объект\n'
        '   Найти другой объект  – в этом разделе, вы можете искать вообще всё что угодно!\n'
        '   Назад  – выйти из режима\n',
        reply_markup=buttons)
    context.user_data['parsing'] = 1
    context.user_data['latest_mode'] = buttons


async def parsing_character(update, _context):
    await update.message.reply_text('Введите имя персонажа из One Piece!')


async def parsing_place(update, _context):
    await update.message.reply_text('Введите название места или острова из One Piece!')


async def parsing_simple_object(update, _context):
    await update.message.reply_text('Введите ваш запрос из вселеной One Piece!')


# ----------------------------------------------------
async def parsing_character_request(update, context):
    await update.message.reply_text('Подождите секундочку...')
    q = Parser().search_character_by_name(request=update.message.text)
    buttons = parsing_buttons(context)
    try:
        text = f'Имя: {q.name}\n\n' \
               f'Награда за голову: {q.bounty}\n\n' \
               f'Возраст: {q.age}\n\n' \
               f'День рождения - {q.birth_date}\n\n' \
               f'Должность: {q.occupations}\n\n' \
               f'Первое появление: {q.first_appearance}\n\n' \
               f'Место проживания: {q.residences}\n\n' \
               f'Членские организации: {q.affiliations}\n\n'
        try:
            open("./tmp.jpg", "wb").write(q.images[0])
            await update.message.reply_photo(photo="./tmp.jpg", caption=text, reply_markup=buttons)
        except IndexError:
            await update.message.reply_text(text, reply_markup=buttons)
    except Exception as e:
        print(e)

        await update.message.reply_text('Прости, но мне не удалось найти что-то похожее.\n' \
                                        'Я искал персонажа, попробуй найти это в другом модуле или ' \
                                        'попробуй воспользоваться случайными терминами!', reply_markup=buttons)
    context.user_data.clear()
    context.user_data['parsing_active'] = 1
    context.user_data['latest_mode'] = buttons


async def parsing_place_request(update, context):
    await update.message.reply_text('Подождите секундочку...')
    q = Parser().search_place_by_name(request=update.message.text)
    buttons = parsing_buttons(context)
    try:
        text = f'Место: {q.name}\n\n' \
               f'Первое появление: {q.first_appearance}\n\n' \
               f'Регион: {q.region}\n\n'
        try:
            open("./tmp.jpg", "wb").write(q.images[0])
            await update.message.reply_photo(photo="./tmp.jpg", caption=text, reply_markup=buttons)
        except IndexError:
            await update.message.reply_text(text, reply_markup=buttons)
    except Exception as e:
        print(e)

        await update.message.reply_text('Прости, но мне не удалось найти что-то похожее.\n' \
                                        'Я искал место, попробуй найти это в другом модуле или ' \
                                        'попробуй воспользоваться случайными терминами!', reply_markup=buttons)
    context.user_data.clear()
    context.user_data['parsing_active'] = 1
    context.user_data['latest_mode'] = buttons


async def parsing_simple_object_request(update, context):
    await update.message.reply_text('Подождите секундочку...')
    q = Parser().search_object(request=update.message.text)
    buttons = parsing_buttons(context)
    try:
        if type(q) == objects.Character:
            text = f'Имя: {q.name}\n\n' \
                   f'Награда за голову: {q.bounty}\n\n' \
                   f'Возраст: {q.age}\n\n' \
                   f'День рождения - {q.birth_date}\n\n' \
                   f'Должность: {q.occupations}\n\n' \
                   f'Первое появление: {q.first_appearance}\n\n' \
                   f'Место проживания: {q.residences}\n\n' \
                   f'Членские организации: {q.affiliations}\n\n'
        elif type(q) == objects.Place:
            text = f'Про {q.name} впервые узнали: {q.first_appearance}\n'
            f'Регион: {q.region}'
        else:
            text = q.name
        try:
            open("./tmp.jpg", "wb").write(q.images[0])
            await update.message.reply_photo(photo="./tmp.jpg", caption=text, reply_markup=buttons)
        except IndexError:
            await update.message.reply_text(text, reply_markup=buttons)
    except Exception as e:
        print(e)

        await update.message.reply_text('Прости, но мне не удалось найти что-то похожее.\n' \
                                        'Это странно, ведь я искал вообще все объекты,' \
                                        ' попробуй найти это в другом модуле или ' \
                                        'попробуй воспользоваться случайными терминами!', reply_markup=buttons)
    context.user_data.clear()
    context.user_data['parsing_active'] = 1
    context.user_data['latest_mode'] = buttons


def q(context):
    return context.user_data['prepared_words_interim'].pop(
        randint(0, len(context.user_data['prepared_words_interim']) - 1))


async def keyboard_of_random_buttons(update, context):
    # prepared_words_interim = context.user_data['prepared_words_interim'] = prepared_words[:]
    many_random_buttons = [[q(context), q(context)], [q(context), q(context)], ['Другие случайные', 'Назад']]
    many_random_buttons = ReplyKeyboardMarkup(many_random_buttons, one_time_keyboard=True)
    await update.message.reply_text('Выберите из предложенного', reply_markup=many_random_buttons)
    context.user_data['latest_mode'] = many_random_buttons
