from aiogram import *
from aiogram.filters import *
from aiogram.types import *
from functions import *
from bot_token import BOT_TOKEN
import sqlite3

# РЕГИСТРАЦИЯ ПЕРЕМЕННОЙ БОТА И ДИСПЕТЧЕРА
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


# СОЗДАНИЕ БАЗЫ ДАННЫХ
db = sqlite3.connect('database.sqlite')
cursor = db.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS data (
    id INTEGER,
    admin BOOL,
    nick TEXT,
    in_game BOOL,
    in_competition BOOL,
    secret INTEGER, 
    attempts INTEGER,
    segment INTEGER,
    games INTEGER,
    wins INTEGER,
    competitions INTEGER,
    comp_wins INTEGER,
    win_percent INTEGER,
    comp_win_percent INTEGER)
''')

db.commit()


# ВОЗВРАЩАЕТ СПИСОК ЛИДЕРОВ ПО УБЫВАНИЮ (СПИСОК ИЗ СПИСКОВ ВИДА [процент побед в соревах, количество игр, ник]
def make_liders():
    liders = []
    for value in cursor.execute(f"SELECT comp_win_percent, comp_wins, nick FROM data"):
        liders.append(value)
    return sorted(liders, reverse=True)


# ВОЗВРАЩАЕТ СПИСОК ЮЗЕРОВ (СПИСКИ ВИДА [количество игр, количество соревнований, количество побед])
def make_users():
    users = []
    for value in cursor.execute(f"SELECT games, competitions, wins FROM data"):
        users.append(value)
    return users


# ЭТА ФУНКЦИЯ ВЫТАСКИВАЕТ ИЗ БД НУЖНУЮ ЯЧЕЙКУ
def sel_data(key: str, message: Message):
    return cursor.execute(f"SELECT {key} FROM data WHERE id = {message.from_user.id}").fetchone()[0]


# ЭТА ФУНКЦИЯ ОБНОВЛЯЕТ В БД НУЖНУЮ ЯЧЕЙКУ
def update_data(key: str, new_info: any, message: Message):
    if isinstance(new_info, str):
        cursor.execute(f"UPDATE data SET {key} = '{new_info}' WHERE id = {message.from_user.id}")
        db.commit()
    else:
        cursor.execute(f"UPDATE data SET {key} = {new_info} WHERE id = {message.from_user.id}")
        db.commit()


# ВНЕДРЕНИЕ КНОПОК В МЕНЮШКЕ И СОЗДАНИЕ МЕНЮШНОЙ КЛАВЫ
competition_button = KeyboardButton(text='Соревноваться!🏆')
play_button = KeyboardButton(text='Играть!🎲')
stat_buttin = KeyboardButton(text='Статистика📖')
liders_button = KeyboardButton(text='Таблица лидеров🏅')
help_keyboard = ReplyKeyboardMarkup(keyboard=[[competition_button, play_button],
                                              [stat_buttin, liders_button]],
                                    resize_keyboard=True)

# ВНЕДРЕНИЕ КНОПОК С ПОПЫТКАМИ И СОЗДАНИЕ ПОПЫТОЧНОЙ КЛАВЫ
button_4 = KeyboardButton(text='(4)')
button_5 = KeyboardButton(text='(5)')
button_6 = KeyboardButton(text='(6)')
button_7 = KeyboardButton(text='(7)')
button_8 = KeyboardButton(text='(8)')
button_9 = KeyboardButton(text='(9)')
attempts_keyboard = ReplyKeyboardMarkup(keyboard=[[button_4, button_5, button_6],
                                                  [button_7, button_8, button_9]],
                                        resize_keyboard=True)

# ВНЕДРЕНИЕ КНОПОК С ДИАПАЗОНАМИ И СОЗДАНИЕ ДИАПАЗОННОЙ КЛАВЫ
button_50 = KeyboardButton(text='(1-50)')
button_75 = KeyboardButton(text='(1-75)')
button_100 = KeyboardButton(text='(1-100)')
button_150 = KeyboardButton(text='(1-150)')
button_200 = KeyboardButton(text='(1-200)')
button_300 = KeyboardButton(text='(1-300)')
segment_keyboard = ReplyKeyboardMarkup(keyboard=[[button_50, button_75, button_100],
                                                 [button_150, button_200, button_300]],
                                       resize_keyboard=True)


# ВНЕДРЕНИЕ КНОПОК С СОГЛАСИЕМ И СОЗДАНИЕ НАЧАНИНАЕМОЙ МЕНЮШКИ
start_button = KeyboardButton(text='Да! Играем😈')
cancel_button = KeyboardButton(text='Нет, я передумал😒')
start_keyboard = ReplyKeyboardMarkup(keyboard=[[start_button, cancel_button]],
                                     resize_keyboard=True)


# ОБРАБОТКА КОМАНДЫ СТАРТ
@dp.message(CommandStart())
async def start_command(message: Message):
    if (cursor.execute(f"SELECT id FROM data WHERE id = {message.from_user.id}")).fetchone() is None:
        cursor.execute("INSERT INTO data VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                       (message.from_user.id, False, '', False, False, 0, 0, 0, 0, 0, 0, 0, 0, 0))
        db.commit()
        await message.answer('Здоров\nЭто микробот для ИТМО\n'
                             'Всё это дело умеет играть в "Угадай число"\n'
                             'Прежде чем я расскажу, что тут вообще происходит, надо зарегестрироваться.\n'
                             'Просто пришли мне свой никнейм.\n'
                             'Только английские буквы и цифры, пж 👉👈')
    elif sel_data("nick", message) == '':
        await message.answer('Зарегайся сначала, прежде чем хоть что-то делать...')
    else:
        await message.answer(f'Привет, {sel_data("nick", message)}\n'
                             f'Ну... ты и так уже в курсе, что тут да как)')
    if sel_data("in_game", message) or sel_data('"in_competition"', message):
        await message.answer('Ты, кстати, вышел из игры сейчас, давай заново)))')
        update_data("in_game", False, message)
        update_data("in_competition", False, message)


# ВЫВОД ИНФЫ И КНОПОК В МЕНЮШКЕ
@dp.message(Command(commands='help'))
async def help_command(message: Message):
    if not sel_data("nick", message) == '':
        if sel_data("in_game", message) or sel_data("in_competition", message):
            await message.answer('Ты, кстати, вышел из игры сейчас.')
            update_data("in_game", False, message)
            update_data("in_competition", False, message)
        await message.answer('Игра заключается в следуюшем: бот загадывает число, а пользователь должен угадать '
                             'его за некоторое количество попыток.\n'
                             'После каждой попытки бот говорит, больше загаданное число или меньше.\n'
                             'В игре есть два режима: соревновательный и тренировочный.\n'
                             'В соревновательном режиме тебе необходимо угадать число от 1 до 100, '
                             'имея в распоряжении 5 попыток.\n'
                             'В этом режиме результаты будут записаны в таблицу лидеров.\n'
                             'В тренировочном режиме тебе доступно различное количество попыток и '
                             'диапазонов загадываемых чисел на выбор.\n'
                             'Результаты будут записаны в отдельную статистику, но не повлияют на соревновательную',
                             reply_markup=help_keyboard)
    else:
        await message.answer('Хватит пытаться сломать бота, зарегайтесь пожалуйста😭😭😭😭😭😭😭😭😭😭😭😭')


# ВЫВОД КНОПОК УПРАВЛЕНИЯ
@dp.message(Command(commands='menu'))
async def help_command(message: Message):
    if sel_data("nick", message) != '':
        await message.answer('Ну держи)', reply_markup=help_keyboard)
        if sel_data("in_game", message) or sel_data("in_competition", message):
            await message.answer('Ты, кстати, вышел из игры сейчас.')
            update_data("in_game", False, message)
            update_data("in_competition", False, message)
    else:
        await message.answer('Хватит пытаться сломать бота, зарегайтесь пожалуйста😭😭😭😭😭😭😭😭😭😭😭😭')


# ОБРАБАТЫВАЕТ ПОДКЛЮЧЕНИЕ АДМИНКИ
@dp.message(F.text == 'I am admin')
async def adminka(message: Message):
    if not sel_data("admin", message):
        update_data("admin", True, message)
        await message.answer('Поздравляю, теперь тебе, как админу, доступна расширенная статистика.')
    else:
        await message.answer('Ты и так админка, зачем еще раз))')


# ПЕРВАЯ РЕПЛИКА ПРИ ВЫБОРЕ СОРЕВНОВАТЕЛЬНОГО РЕЖИМА
@dp.message(F.text == 'Соревноваться!🏆')
async def competition(message: Message):
    if sel_data("nick", message) != '':
        await message.answer('Ты выбрал соревновательный режим.', reply_markup=ReplyKeyboardRemove())
        if not sel_data("in_competition", message):
            update_data("in_competition", True, message)
            update_data("segment", 100, message)
            update_data("secret", generation(100), message)
            update_data("attempts", 5, message)
            await message.answer('Я загадал число от 1 до 100\n'
                                 'Отправляй мне числа, а я буду говорить, больше загаданное или меньше.\n'
                                 'У тебя есть 5 попыток.')
        else:
            await message.answer('я НЕ ЗНАЮ, как это произошло, но как бы эм... ты и так в игре, так что нечего тут '
                                 'бота ломать. Давай заново')
            if sel_data("in_game", message) or sel_data("in_competition", message):
                update_data("in_game", False, message)
                update_data("in_competition", False, message)
    else:
        await message.answer('Хватит пытаться сломать бота, зарегайтесь пожалуйста😭😭😭😭😭😭😭😭😭😭😭😭')


# СЛУЧАЕТСЯ ВЫБОР ДИАПАЗОНА ЧИСЕЛ НА ИГРУ
@dp.message(F.text == 'Играть!🎲')
async def segment(message: Message):
    if sel_data("nick", message) != '':
        await message.answer(text='Ты выбрал тренировочный режим.', reply_markup=ReplyKeyboardRemove())
        await message.answer('Выбери диапазон загадываемых чисел:', reply_markup=segment_keyboard)
        if sel_data("in_game", message) or sel_data("in_competition", message):
            await message.answer('Ты, кстати, вышел из игры сейчас, давай заново)))')
            update_data("in_game", False, message)
            update_data("in_competition", False, message)
    else:
        await message.answer('Хватит пытаться сломать бота, зарегайтесь пожалуйста😭😭😭😭😭😭😭😭😭😭😭😭')


# СЛУЧАЕТСЯ ВЫБОР КОЛИЧЕСТВА ПОПЫТОК НА ИГРУ
@dp.message(F.text.in_(['(1-50)', '(1-75)', '(1-100)', '(1-150)', '(1-200)', '(1-300)']))
async def attempts(message: Message):
    if sel_data("nick", message) != '':
        update_data("segment", int(str(message.text)[3:-1]), message)
        await message.answer('Принято!', reply_markup=ReplyKeyboardRemove())
        await message.answer('Теперь выбери количество попыток на игру:', reply_markup=attempts_keyboard)
        if sel_data("in_game", message) or sel_data("in_competition", message):
            await message.answer('Ты, кстати, вышел из игры сейчас, давай заново)))')
            update_data("in_game", False, message)
            update_data("in_competition", False, message)
    else:
        await message.answer('Хватит пытаться сломать бота, зарегайтесь пожалуйста😭😭😭😭😭😭😭😭😭😭😭😭')


# ПРОИСХОДИТ ПОДТВЕРЖДЕНИЕ ВЫБОРА ИГРОКА
@dp.message(F.text.in_(['(4)', '(5)', '(6)', '(7)', '(8)', '(9)']))
async def attempts(message: Message):
    if sel_data("nick", message) != '':
        update_data("attempts", int(str(message.text)[1:-1]), message)
        await message.answer(f'Ты выбрал игру в диапазоне чисел от 1 до {sel_data("segment", message)} '
                             f'c {sel_data("attempts", message)} попытками в запасе.\n',
                             reply_markup=ReplyKeyboardRemove())
        await message.answer('Всё верно?', reply_markup=start_keyboard)
        if sel_data("in_game", message) or sel_data("in_competition", message):
            await message.answer('Ты, кстати, вышел из игры сейчас, давай заново)))')
            update_data("in_game", False, message)
            update_data("in_competition", False, message)
    else:
        await message.answer('Хватит пытаться сломать бота, зарегайтесь пожалуйста😭😭😭😭😭😭😭😭😭😭😭😭')


# РЕАКЦИЯ НА ОТМЕНУ ИГРЫ
@dp.message(F.text == 'Нет, я передумал😒')
async def beginning_play(message: Message):
    if sel_data("nick", message) != '':
        await message.answer('А жаль(', reply_markup=ReplyKeyboardRemove())
        if sel_data("in_game", message) or sel_data("in_competition", message):
            update_data("in_game", False, message)
            update_data("in_competition", False, message)
    else:
        await message.answer('Хватит пытаться сломать бота, зарегайтесь пожалуйста😭😭😭😭😭😭😭😭😭😭😭😭')


# РЕАКЦИЯ НА НАЧАЛО ИГРЫ
@dp.message(F.text == 'Да! Играем😈')
async def beginning_play(message: Message):
    if sel_data("nick", message) != '':
        await message.answer(f'Ура!', reply_markup=ReplyKeyboardRemove())
        if not sel_data("in_game", message):
            update_data("in_game", True, message)
            update_data("secret", generation(sel_data("segment", message)), message)
            await message.answer(f'Я загадал число от 1 до {sel_data("segment", message)}\n'
                                 f'Отправляй мне числа, а я буду говорить, больше загаданное или меньше.')
        else:
            await message.answer('я НЕ ЗНАЮ, как это произошло, но как бы эм... ты и так в игре, так что нечего тут '
                                 'бота ломать. Давай заново')
            update_data("in_game", False, message)
            update_data("in_competition", False, message)
    else:
        await message.answer('Хватит пытаться сломать бота, зарегайтесь пожалуйста😭😭😭😭😭😭😭😭😭😭😭😭')


# ВЫВОДИТ ОБШУЮ СТАТИСТИКУ ПОЛЬЗОВАТЕЛЯ
@dp.message(F.text == 'Статистика📖')
async def statistics(message: Message):
    if sel_data("nick", message) != '':
        if sel_data("in_game", message) or sel_data("in_competition", message):
            await message.answer('Ты, кстати, вышел из игры сейчас, давай заново)))')
            update_data("in_game", False, message)
            update_data("in_competition", False, message)
        if sel_data("games", message) != 0:
            await message.answer(f'Ты провёл {sel_data("games", message)} '
                                 f'{quantity_of_games(sel_data("games", message))}.\n'
                                 f'Из них '
                                 f'{round(sel_data("wins", message) / sel_data("games", message) * 100, 1)}'
                                 f'% побед.',
                                 reply_markup=ReplyKeyboardRemove())
        else:
            await message.answer('Ты ещё даже ни разу не сыграл, нечего тебе тут смотреть)',
                                 reply_markup=ReplyKeyboardRemove())
    else:
        await message.answer('Хватит пытаться сломать бота, зарегайтесь пожалуйста😭😭😭😭😭😭😭😭😭😭😭😭')
    if sel_data("admin", message) and sel_data("games", message) != 0:
        all_games = 0
        all_competitions = 0
        all_vyctory_percents = 0
        all_vyctories = 0
        counter = 0
        users = make_users()
        for i in users:
            all_games += i[0]
            all_competitions += i[1]
            all_vyctories += i[2]
        liders = make_liders()
        for j in liders:
            all_vyctory_percents += j[0]
            if j[0] != 0:
                counter += 1
        if counter != 0:
            average_percent = all_vyctory_percents / counter
        else:
            average_percent = 0
        average_vyctories = round(all_vyctories / all_games * 100, 3)
        await message.answer(f'Общая статистика:\n'
                             f'Игроков: {len(liders)}\n'
                             f'Всего игр: {all_games}\n'
                             f'Средний процент побед: {average_vyctories}%\n'
                             f'Всего соревнований: {all_competitions}\n'
                             f'Средний процент побед: {round(average_percent, 3)}%\n')
        text = ''
        for j in range(len(liders)):
            text += f'{j + 1}: {liders[j][2]} - {liders[j][0]}% побед\n'
        await message.answer('Таблица пользователей:\n' + text)


# ВЫВОД ТАБЛИЦЫ ЛИДЕРОВ
@dp.message(F.text == 'Таблица лидеров🏅')
async def table_lider(message: Message):
    if sel_data("nick", message) != '':
        if sel_data("in_game", message) or sel_data("in_competition", message):
            await message.answer('Ты, кстати, вышел из игры сейчас, давай заново)))')
            update_data("in_game", False, message)
            update_data("in_competition", False, message)
        if sel_data("competitions", message) != 0:
            liders = make_liders()
            nicks = []
            for i in liders:
                nicks.append(i[2])
            this_user_number = nicks.index(sel_data("nick", message))
            await message.answer(f'Количество игроков: {len(liders)}.\n'
                                 f'Лидером является {liders[0][2]} с результатом \n'
                                 f'{round(liders[0][0], 1)}% побед в '
                                 f'{liders[0][1]} {finished_games(liders[0][1])}\n'
                                 f'\n'
                                 f'Ты находишься на '
                                 f'{this_user_number + 1}-й позиции с результатом \n'
                                 f'{round(liders[this_user_number][0], 1)}% побед в '
                                 f'{liders[this_user_number][1]} '
                                 f'{finished_games(liders[this_user_number][1])}',
                                 reply_markup=ReplyKeyboardRemove())
        else:
            await message.answer('Ты ещё даже ни разу не соревновался, нечего тебе тут смотреть)',
                                 reply_markup=ReplyKeyboardRemove())
    else:
        await message.answer('Хватит пытаться сломать бота, зарегайтесь пожалуйста😭😭😭😭😭😭😭😭😭😭😭😭')


# ОБРАБОТКА ЧИСЕЛ ВО ВРЕМЯ ИГРЫ
@dp.message(lambda x: x.text and x.text.isdigit() and 1 <= int(x.text) <= 300)
async def numbers(message: Message):
    if sel_data("nick", message) != '':
        number = int(message.text)
        if number > sel_data("segment", message):
            await message.answer(f'Эээ... вообще-то верхняя граница - {sel_data("segment", message)}.')
        elif sel_data("in_game", message) or sel_data("in_competition", message):
            if number == sel_data("secret", message):
                await message.answer('Круто, круто. Это победа, поздравляю!)\n'
                                     'Чтобы сыграть ещё раз, костыльно снова вызови команду '
                                     '/menu и приступай к выборам.')
                update_data("wins", sel_data("wins", message) + 1, message)
                update_data("games", sel_data("games", message) + 1, message)
                if sel_data("in_competition", message):
                    update_data("comp_wins", sel_data("comp_wins", message) + 1, message)
                    update_data("competitions", sel_data("competitions", message) + 1, message)
                    update_data("comp_win_percent",
                                round(sel_data("comp_wins", message) /
                                      sel_data("competitions", message) *
                                      100),
                                message)
                update_data("in_game", False, message)
                update_data("in_competition", False, message)
            elif number > sel_data("secret", message):
                update_data("attempts", sel_data("attempts", message) - 1, message)
                if sel_data("attempts", message) > 0:
                    await message.answer('Нет, не угадал, моё число меньше.')
            else:
                update_data("attempts", sel_data("attempts", message)- 1, message)
                if sel_data("attempts", message) > 0:
                    await message.answer('Нет, не угадал, моё число больше.')
            if sel_data("attempts", message) == 0:
                update_data("games", sel_data("games", message) + 1, message)
                if sel_data("in_competition", message):
                    update_data("competitions", sel_data("competitions", message) + 1, message)
                    update_data("comp_win_percent",
                                round(sel_data("wins", message) /
                                      sel_data("games", message) *
                                      100),
                                message)
                await message.answer('К сожалению, ты проиграл((\n'
                                     f'Было загадано число {sel_data("secret", message)}.\n'
                                     'Чтобы сыграть ещё раз, костыльно '
                                     'снова вызови команду /menu и приступай к выборам.')
                update_data("in_game", False, message)
                update_data("in_competition", False, message)
        else:
            await message.answer('Игра ещё не началась извините')
    else:
        await message.answer('Хватит пытаться сломать бота, зарегайтесь пожалуйста😭😭😭😭😭😭😭😭😭😭😭😭')


@dp.message(F.content_type != 'text')
async def not_text(message: Message):
    if sel_data("nick", message) == '':
        await message.answer('Хватит пытаться сломать бота, зарегайтесь пожалуйста😭😭😭😭😭😭😭😭😭😭😭😭')
    else:
        await message.answer('Ну прикольно, это не текст, я это отлавливаю просто так, заодно с защитой от идиотов)')


# ОБРАБОТКА ВСЯКОЙ ГАДОСТИ + РЕГИСТРАЦИЯ
@dp.message()
async def other_messages(message: Message):
    if sel_data("nick", message) == '':
        liders = make_liders()
        nicks = []
        for i in liders:
            nicks.append(i[2])
        if message.text not in nicks and checking_nickname(message.text) and message.text != '':
            update_data("nick", message.text, message)
            await message.answer(f'Поздравляю с успешной регистрацией, {sel_data("nick", message)}\n'
                                 f'Теперь можно смело жмякать /help')
        elif message.text in liders:
            await message.answer('К сожалению, игрок с таким именем уже зарегистрировался, попробуйте другое.')
        elif not checking_nickname(message.text):
            await message.answer('Используй только английские буквы и цифры ПОЖАЛУЙСТА.')
        else:
            await message.answer('Я не знаю, как можно было добиться это найдписи, но ПОЖАЛУЙСТА ЗАРЕГАЙСЯ!!!')
    elif sel_data("in_game", message) or sel_data("in_competition", message):
        if is_number(message.text):
            await message.answer(f'Сорян, но только целые числа от 1 до {sel_data("segment", message)}.')
        else:
            await message.answer(f'Ну эй, мы же играем((')
    else:
        await message.answer('Сорян, не настолько я всё продумал(')

if __name__ == '__main__':
    dp.run_polling(bot)
