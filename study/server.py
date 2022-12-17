#server.py




### #server.py


"""Сервер Telegram бота, запускаемый непосредственно"""

import logging

import os

  

import aiohttp

from aiogram import Bot, Dispatcher, executor, types

  

import exceptions

import expenses

  

from categories import Categories

from middlewares import AccessMiddleware

  
  
  

logging.basicConfig(level=logging.INFO)

  

API_TOKEN = os.getenv("API_TOKEN")

#PROXY_URL = os.getenv("TELEGRAM_PROXY_URL")

#PROXY_AUTH = aiohttp.BasicAuth(

#    login=os.getenv("TELEGRAM_PROXY_LOGIN"), #    password=os.getenv("TELEGRAM_PROXY_PASSWORD")

#)

ACCESS_ID = os.getenv("ACCES_ID")

  

bot = Bot(token=API_TOKEN)#, proxy=PROXY_URL, proxy_auth=PROXY_AUTH)

dp = Dispatcher(bot)

dp.middleware.setup(AccessMiddleware(ACCESS_ID))

  
  

@dp.message_handler(commands=['start', 'help'])

async def send_welcome(message: types.Message):

    """Отправляет приветственное сообщение и помощь по боту"""

    await message.answer(

        "Бот для учёта финансов\n\n"

        "Добавить расход: 250 такси\n"

        "Сегодняшняя статистика: /today\n"

        "За текущий месяц: /month\n"

        "Последние внесённые расходы: /expenses\n"

        "Категории трат: /categories")

  
  

@dp.message_handler(lambda message: message.text.startswith('/del'))

async def del_expense(message: types.Message):

    """Удаляет одну запись о расходе по её идентификатору"""

    row_id = int(message.text[4:])

    expenses.delete_expense(row_id)

    answer_message = "Удалил"

			 await message.answer(answer_message)

  
  

@dp.message_handler(commands=['categories'])

async def categories_list(message: types.Message):

    """Отправляет список категорий расходов"""

    categories = Categories().get_all_categories()

    answer_message = "Категории трат:\n\n* " +\

            ("\n* ".join([c.name+' ('+", ".join(c.aliases)+')' for c in categories]))

    await message.answer(answer_message)

  
  

@dp.message_handler(commands=['today'])

async def today_statistics(message: types.Message):

    """Отправляет сегодняшнюю статистику трат"""

    answer_message = expenses.get_today_statistics()

    await message.answer(answer_message)

  
  

@dp.message_handler(commands=['month'])

async def month_statistics(message: types.Message):

    """Отправляет статистику трат текущего месяца"""

    answer_message = expenses.get_month_statistics()

    await message.answer(answer_message)

  
  

@dp.message_handler(commands=['expenses'])

async def list_expenses(message: types.Message):

    """Отправляет последние несколько записей о расходах"""

    last_expenses = expenses.last()

    if not last_expenses:

        await message.answer("Расходы ещё не заведены")

        return

  

    last_expenses_rows = [

        f"{expense.amount} uah. на {expense.category_name} — нажми "

        f"/del{expense.id} для удаления"

        for expense in last_expenses]

    answer_message = "Последние сохранённые траты:\n\n* " + "\n\n* "\

            .join(last_expenses_rows)

    await message.answer(answer_message)

  
  

@dp.message_handler()

async def add_expense(message: types.Message):

    """Добавляет новый расход"""

    try:

        expense = expenses.add_expense(message.text)

    except exceptions.NotCorrectMessage as e:

        await message.answer(str(e))

        return

    answer_message = (

        f"Добавлены траты {expense.amount} uah на {expense.category_name}.\n\n"

        f"{expenses.get_today_statistics()}")

    await message.answer(answer_message)

  
  

if __name__ == '__main__':

    executor.start_polling(dp, skip_updates=True)

  
  
  
  
  

### db.py

  

import os

from typing import Dict, List, Tuple

  

import psycopg2

from psycopg2 import sql

  

DATABASE_URL = os.environ['DATABASE_URL']

  

con = psycopg2.connect(DATABASE_URL, sslmode='require')

cur = con.cursor()

  

def insert(table: str, column_values: Dict):

    columns =  column_values.keys()

    values = tuple(column_values.values())

    A = ['%s']

    #placeholders = ",".join(A * len(column_values.keys()))

    print(table)

    print(columns)

    print(values)

    #print(placeholders)

    #

    query = sql.SQL("insert into {table}({columns}) values ({placeholder})").format(

        table = sql.Identifier(table),

        columns = sql.SQL(', ').join(map(sql.Identifier, columns)),

        placeholder = sql.SQL(', ').join(sql.Placeholder() * len(values)))

    print(query.as_string(con), values)

  
  

    con.commit()

  
  

    cur.execute(query, values)

       # cur.executemany(insert_query, values)

    con.commit()

    return

  

def fetchall(table: str, columns: List[str]) -> List[Tuple]:

    columns_joined = ", ".join(columns)

    print(table, columns_joined)

    cur.execute(f"SELECT {columns_joined} FROM {table}")

    rows = cur.fetchall()

    result = []

    for row in rows:

        print(row[0])

        dict_row = {}

        for index, column in enumerate(columns):

            dict_row[column] = row[index]

        result.append(dict_row)

        print(result)

    return result

  
  
  

def delete(table: str, row_id: int) -> None:

    row_id = int(row_id)

    cur.execute(f"delete from {table} where id={row_id}")

    con.commit()

  

def get_cursor():

  

    print("Connection DB succesfuly!")

    return cur

  
  

def _init_db():

    """Инициализирует БД"""

    with open("createdb.sql", "r") as f:

        sql = f.read()

  

    cur.execute(sql)

    con.commit()

  

def check_db():

    print("New air good!")

    try:

        cur.execute("SELECT version();")

        rows = cur.fetchall()

        for row in rows:

            print(row[0])

        print("cursor go!")

        check_db_exists()

  

    except Exception as err:

        print(err)

  
  

def check_db_exists():

    """Проверяет, инициализирована ли БД, если нет — инициализирует"""

    #try:

    print("Приступаем к инициализации!")

    cur.execute("select 1 from information_schema.tables where table_name=%s", ('category',))

    table_exists = cur.fetchall()

    for row in table_exists:

        print(row[0])

    print("I think, init ok!" )

    if table_exists:

        print("Таблица сущесвует, работаем!")

       # delete("expense", 0)

        return

    else:

        print("Таблицы нет, создаем!")

        _init_db()

    #except:

     #   print("Нифига не получилось, пока не понятно что.")

  

print("Hello, world!")

check_db()

print("check go!")

  

### #creatdb.sql

  

create table budget(

    codename varchar(255) primary key,

    daily_limit integer

);

  

create table category(

    codename varchar(255) primary key,

    name varchar(255),

    is_base_expense boolean,

    aliases text

);

  

create table expense(

    id serial primary key,

    amount integer,

    created date,

    category_codename varchar(255),

    raw_text text,

       FOREIGN KEY(category_codename) REFERENCES category(codename)

);

  
  
  

insert into category(codename, name, is_base_expense, aliases) values ('products', 'продукты', true, 'еда'),

    ('coffee', 'кофе', true, '.'),

    ('dinner', 'обед', true, 'столовая, ланч, бизнес-ланч, бизнес ланч'),

    ('cafe', 'кафе', true, 'ресторан, рест, мак, макдональдс, макдак, kfc, ilpatio, il patio'),

    ('transport', 'общ. транспорт', false, 'метро, автобус, metro'),

    ('taxi', 'такси', false, 'яндекс такси, yandex taxi'),

    ('phone', 'телефон', false, 'теле2, связь'),

    ('books', 'книги', false, 'литература, литра, лит-ра'),

    ('internet', 'интернет', false, 'инет, inet'),

    ('subscriptions', 'подписки', false, 'подписка'),

    ('other', 'прочее', true, '.');

  

insert into budget(codename, daily_limit) values ('base', 500);

  
  

### categories.py

"""Работа с категориями расходов"""

from typing import Dict, List, NamedTuple

  

import db

  
  

class Category(NamedTuple):

    """Структура категории"""

    codename: str

    name: str

    is_base_expense: bool

    aliases: List[str]

  
  

class Categories:

    def __init__(self):

        self._categories = self._load_categories()

  

    def _load_categories(self) -> List[Category]:

        """Возвращает справочник категорий расходов из БД"""

        categories = db.fetchall(

            "category", "codename name is_base_expense aliases".split()

        )

        categories = self._fill_aliases(categories)

        return categories

  

    def _fill_aliases(self, categories: List[Dict]) -> List[Category]:

        """Заполняет по каждой категории aliases, то есть возможные

        названия этой категории, которые можем писать в тексте сообщения.

        Например, категория «кафе» может быть написана как cafe,

        ресторан и тд."""

        categories_result = []

        for index, category in enumerate(categories):

            aliases = category["aliases"].split(",")

            aliases = list(filter(None, map(str.strip, aliases)))

            aliases.append(category["codename"])

            aliases.append(category["name"])

            categories_result.append(Category(

                codename=category['codename'],

                name=category['name'],

                is_base_expense=category['is_base_expense'],

                aliases=aliases

            ))

        return categories_result

  

    def get_all_categories(self) -> List[Dict]:

        """Возвращает справочник категорий."""

        return self._categories

  

    def get_category(self, category_name: str) -> Category:

        """Возвращает категорию по одному из её алиасов."""

        finded = None

        other_category = None

        for category in self._categories:

            if category.codename == "other":

                other_category = category

            for alias in category.aliases:

                if category_name in alias:

                    finded = category

        if not finded:

            finded = other_category

        return finded

  

### exceptions.py

"""Кастомные исключения, генерируемые приложением"""

  
  

class NotCorrectMessage(Exception):

    """Некорректное сообщение в бот, которое не удалось распарсить"""

    pass

  

### expenses.py

""" Работа с расходами — их добавление, удаление, статистика"""

import datetime

import re

from typing import List, NamedTuple, Optional

  

import pytz

  

import db

import exceptions

from categories import Categories

  
  

class Message(NamedTuple):

    """Структура распаршенного сообщения о новом расходе"""

    amount: int

    category_text: str

  
  

class Expense(NamedTuple):

    """Структура добавленного в БД нового расхода"""

    id: Optional[int]

    amount: int

    category_name: str

  
  

def add_expense(raw_message: str) -> Expense:

    print(raw_message)

    """Добавляет новое сообщение.

    Принимает на вход текст сообщения, пришедшего в бот."""

    parsed_message = _parse_message(raw_message)

    category = Categories().get_category(

        parsed_message.category_text)

    inserted_row_id = db.insert("expense", {

        "amount": parsed_message.amount,

        "created": _get_now_formatted(),

        "category_codename": category.codename,

        "raw_text": raw_message

    })

    return Expense(id=None,

                   amount=parsed_message.amount,

                   category_name=category.name)

  
  

def get_today_statistics() -> str:

    """Возвращает строкой статистику расходов за сегодня"""

    cursor = db.get_cursor()

    cursor.execute("select sum(amount)"

                   "from expense where date(created)=date_trunc('Days', Now())")

    result = cursor.fetchone()

    if not result[0]:

        return "Сегодня ещё нет расходов"

    all_today_expenses = result[0]

    cursor.execute("select sum(amount)"

                   "from expense where date(created)=date_trunc('Days', Now()) "

                   "and category_codename in (select codename "

                   "from category where is_base_expense=true)")

    result = cursor.fetchone()

    base_today_expenses = result[0] if result[0] else 0

    return (f"Расходы сегодня:\n"

            f"всего — {all_today_expenses} uah.\n"

            f"базовые — {base_today_expenses} uah. из {_get_budget_limit()} uah.\n\n"

            f"За текущий месяц: /month")

  
  

def get_month_statistics() -> str:

    """Возвращает строкой статистику расходов за текущий месяц"""

    now = _get_now_datetime()

    first_day_of_month = f'{now.year:04d}-{now.month:02d}-01'

    cursor = db.get_cursor()

    cursor.execute(f"select sum(amount) "

                   f"from expense where date(created) >= '{first_day_of_month}'")

    result = cursor.fetchone()

    if not result[0]:

        return "В этом месяце ещё нет расходов"

    all_today_expenses = result[0]

    cursor.execute(f"select sum(amount) "

                   f"from expense where date(created) >= '{first_day_of_month}' "

                   f"and category_codename in (select codename "

                   f"from category where is_base_expense=true)")

    result = cursor.fetchone()

    base_today_expenses = result[0] if result[0] else 0

    return (f"Расходы в текущем месяце:\n"

            f"всего — {all_today_expenses} uah.\n"

            f"базовые — {base_today_expenses} uah. из "

            f"{now.day * _get_budget_limit()} uah.")

  
  

def last() -> List[Expense]:

    """Возвращает последние несколько расходов"""

    cursor = db.get_cursor()

    cursor.execute(

        "select e.id, e.amount, c.name "

        "from expense e left join category c "

        "on c.codename=e.category_codename "

        "order by created desc limit 10")

    rows = cursor.fetchall()

    last_expenses = [Expense(id=row[0], amount=row[1], category_name=row[2]) for row in rows]

    return last_expenses

  
  

def delete_expense(row_id: int) -> None:

    """Удаляет сообщение по его идентификатору"""

    db.delete("expense", row_id)

  
  

def _parse_message(raw_message: str) -> Message:

    """Парсит текст пришедшего сообщения о новом расходе."""

    regexp_result = re.match(r"([\d ]+) (.*)", raw_message)

    if not regexp_result or not regexp_result.group(0) \

            or not regexp_result.group(1) or not regexp_result.group(2):

        raise exceptions.NotCorrectMessage(

            "Не могу понять сообщение. Напишите сообщение в формате, "

            "например:\n1500 метро")

  

    amount = regexp_result.group(1).replace(" ", "")

    category_text = regexp_result.group(2).strip().lower()

    return Message(amount=amount, category_text=category_text)

  
  

def _get_now_formatted() -> str:

    """Возвращает сегодняшнюю дату строкой"""

    return _get_now_datetime().strftime("%Y-%m-%d %H:%M:%S")

  
  

def _get_now_datetime() -> datetime.datetime:

    """Возвращает сегодняшний datetime с учётом времненной зоны Мск."""

    tz = pytz.timezone("Europe/Moscow")

    now = datetime.datetime.now(tz)

    return now

  
  

def _get_budget_limit() -> int:

    """Возвращает дневной лимит трат для основных базовых трат"""

    return db.fetchall("budget", ["daily_limit"])[0]["daily_limit"]

  

### middlewares.py

"""Аутентификация — пропускаем сообщения только от одного Telegram аккаунта"""

from aiogram import types

from aiogram.dispatcher.handler import CancelHandler

from aiogram.dispatcher.middlewares import BaseMiddleware

  
  

class AccessMiddleware(BaseMiddleware):

    def __init__(self, access_id: int):

        self.access_id = access_id

        super().__init__()

  

    async def on_process_message(self, message: types.Message, _):

        if int(message.from_user.id) != int(self.access_id):

            await message.answer("Access Denied")

            raise CancelHandler()

  

### Pipfile

\[[source]]

name = "pypi"

url = "https://pypi.org/simple"

verify_ssl = true

  

[dev-packages]

  

[packages]

aiogram = "==2.8"

aiohttp = "==3.6.2"

async-timeout = "==3.0.1"

attrs = "==19.3.0"

certifi = "==2020.4.5.1"

chardet = "==3.0.4"

idna = "==2.9"

multidict = "==4.7.5"

pytz = "==2020.1"

yarl = "==1.4.2"

Babel = "==2.8.0"

psycopg2-binary = "*"

  

[requires]

python_version = "3.8"

  

### requirements.txt

aiogram==2.4

aiohttp==3.6.2

async-timeout==3.0.1

attrs==19.3.0

Babel==2.7.0

certifi==2019.11.28

chardet==3.0.4

idna==2.8

multidict==4.7.3

pytz==2019.3

yarl==1.4.2

  

### runtime.txt

python-3.9.13