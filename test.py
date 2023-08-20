import objects
from parser import Parser
def parsing_character_request(z):
    print('Подождите секундочку...')
    q = Parser().search_character_by_name(request=z)
    print(type(q))
    if type(q) != type([]):
        text = f'Имя: {q.name}\n\n' \
               f'Возраст: {q.age}\n\n' \
               f'День рождения - {q.birth_date}\n\n' \
               f'Должность: {q.occupations}\n\n' \
               f'Первое появление: {q.first_appearance}\n\n' \
               f'Место проживания: {q.residences}\n\n' \
               f'Членские организации: {q.affiliations}\n\n'
        try:
            open("./tmp.jpg", "wb").write(q.images[0])
        except IndexError:
            print('no foto')
        print(text)
    else:
        a = Parser().search_object(request=z)
        type(a)
        try:
            open("./tmp.jpg", "wb").write(a.images[0])
        except IndexError:
            print('no foto')
        print(a)
        print(a.name)

#parsing_character_request('эльбаф')
#       Наитамие-Норида Слон
q = Parser().search_object(request='слон')
print(type(q))
if type(q) == objects.Character:
    text = f'Имя: {q.name}\n\n' \
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
    text = f'{q.name} (на японском - {q.jap_name})'
try:
    open("./tmp.jpg", "wb").write(q.images[0])
except IndexError:
    print('no foto')
print(text)