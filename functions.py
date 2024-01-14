from random import randint


# ПРОВЕРКА КОРРЕКТНОСТИ НИКНЕЙМА
def checking_nickname(nick: str):
    for i in nick:
        if not (48 <= ord(i) <= 57 or 65 <= ord(i) <= 90 or 97 <= ord(i) <= 122):
            return False
    return True


# ФУНКЦИЯ, КОТОРАЯ ВЫКИДЫВАЕТ ПРАВИЛЬНОЕ СКЛОНЕНИЕ СЛОВА "ИГРА"
def quantity_of_games(a: int):
    if a % 10 == 1 and a % 100 != 11:
        return 'игру'
    elif a % 10 in [2, 3, 4] and not(11 <= a % 100 <= 19):
        return 'игры'
    else:
        return 'игр'


# ФУНКЦИЯ, КОТОРАЯ ВЫКИДЫВАЕТ ПРАВИЛЬНОЕ СКЛОНЕНИЕ СЛОВОСОЧЕТАНИЯ "ПРОВЕДЕННЫХ ИГРАХ"
def finished_games(a: int):
    if a == 1:
        return 'проведённой игре.'
    else:
        return 'проведённых играх.'


# ГЕНЕРАЦИЯ СЕКРЕТНОГО ЧИСЛА
def generation(end) -> int:
    return randint(1, end)


# ПРОВЕРКА НАЛИЧИЯ ЧИСЛА В СООБЩЕНИИ
def is_number(x):
    x = str(x)
    x = x.replace(',', '.')
    if x.count('.') <= 1 and not (x.startswith('.')):
        if x.startswith('-'):
            x = x.replace('.', '')
            return x[1:].isdigit()
        else:
            x = x.replace('.', '')
            return x.isdigit()
    else:
        return False
