import config
import telebot
from telebot import types
from datetime import datetime

from sqlalchemy import create_engine, Column, Integer, String, Boolean,ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, declarative_base

bot = telebot.TeleBot(token=config.TOKEN) #токен
engine = create_engine('sqlite:///salon.db', echo=True)
Base = declarative_base()


# Определение модели записи
class Record(Base):
    __tablename__ = 'record'
    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(String)
    service = Column(String)
    master = Column(String)
    visitor_id = Column(String, ForeignKey('user.userId'))

    # Добавим обратное отношение к модели User
    visitor = relationship('User', back_populates='records')

    def __init__(self, date, service, master, visitor=None):
        self.date = date
        self.master = master
        self.service = service
        self.visitor = visitor


# Определение модели пользователя
class User(Base):
    __tablename__ = 'user'

    userId = Column(String, primary_key=True)
    name = Column(String)

    # Добавим обратное отношение к модели Record
    records = relationship('Record', back_populates='visitor')

    def __init__(self, userId, name):
        self.userId = userId
        self.name = name


# Создание таблиц
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()

def insert_record(date, service, master, visitor=None):
    # Добавление записи
    new_record = Record(date=date, master=master, service=service,  visitor=visitor)
    session.add(new_record)
    session.commit()


def update_visitor(date, service, master, visitor):
    # Поле visitor меняем на данные пользователя
    record = session.query(Record).filter_by(date=date, service=service, master=master, visitor='-').first()
    if record:
        record.visitor = visitor
        session.commit()

def pay_record(date, service, master, visitor):
    # Добавление информации о записи на услугу в таблицу
    date_today = datetime.now().date()
    pay_record = PayRecord(date_today=date_today, date=date, service=service, master=master, visitor=visitor)
    session.add(pay_record)
    session.commit()

def record_show(date):
    # Вывод записи
    rows = session.query(Record.service, Record.master).filter_by(date=date).distinct().all()
    rasp_list = []
    for row in rows:
        service, master = row
        rasp_list.append(f" Услуга {service}, специалист: {master}")
    return rasp_list


"""insert_record('10.11.23', 'Волосы', 'Петрова Анна Павловна')
insert_record('20.11.23', 'Волосы', 'Петрова Анна Павловна')
insert_record('24.11.23', 'Волосы', 'Петрова Анна Павловна')
insert_record('26.11.23', 'Волосы', 'Петрова Анна Павловна')
insert_record('10.11.23', 'Депиляция', 'Лукъянова Наталья Олеговна')
insert_record('20.11.23', 'Депиляция', 'Лукъянова Наталья Олеговна')
insert_record('24.11.23', 'Депиляция', 'Лукъянова Наталья Олеговна')
insert_record('26.11.23', 'Депиляция', 'Лукъянова Наталья Олеговна')
insert_record('10.11.23', 'Маникюр', 'Терентьева Мария Петровна')
insert_record('20.11.23', 'Маникюр', 'Терентьева Мария Петровна')
insert_record('24.11.23', 'Маникюр', 'Терентьева Мария Петровна')
insert_record('26.11.23', 'Маникюр', 'Терентьева Мария Петровна')
insert_record('10.11.23', 'Макияж', 'Цветкова Ольга Алексеевна')
insert_record('20.11.23', 'Макияж', 'Цветкова Ольга Алексеевна')
insert_record('24.11.23', 'Макияж', 'Цветкова Ольга Алексеевна')
insert_record('26.11.23', 'Макияж', 'Цветкова Ольга Алексеевна')
"""

def record_create():
    record = Record(name='example', date='2021-01-01', time='12:00PM')

    session.add(record)

def create_usertable():
    Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()

# Вывод таблицы с записью
records = session.query(Record).all()
for record in records:
    print(record.date, record.service, record.master, record.visitor)


"""
insert_record('10.11.23', 'Волосы', 'Петрова Анна Павловна')
insert_record('20.11.23', 'Депиляция', 'Лукъянова Наталья Олеговна')
insert_record('24.11.23', 'Маникюр', 'Терентьева Мария Петровна')
insert_record('26.11.23', 'Макияж', 'Цветкова Ольга Алексеевна')
"""

session.commit()




@bot.message_handler(commands=['start']) #декоратор, обрабатываем команду старт
def start(call):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    botton1 = types.KeyboardButton('Записаться')
    botton2 = types.KeyboardButton('Отменить запись')
    markup.add(botton1, botton2)
    botton4 = types.InlineKeyboardButton('Перейти на сайт', url='https://nataxtare.github.io/sweet_lemon_site/')

    botton5 = types.KeyboardButton('Прайс')
    markup.add(botton4, botton5)
    bot.send_message(call.chat.id, f'Здравствуйте, {call.from_user.first_name}! \nВас приветствует салон красоты Sweety Lemon.', reply_markup=markup)

    ids = session.query(User.userId).all()
    if (str(call.chat.id),) not in ids:
        bot.send_message(call.chat.id,
                         'Перед тем, как начать пользоваться ботом, пожалуйста, укажите свои полные фамилию, имя и отчество.')
        bot.register_next_step_handler(call, new_name)


@bot.message_handler(content_types=['text'])
def menu(call):
    if call.text == 'Записаться':
        markup = types.InlineKeyboardMarkup()
        dates = session.query(Record.date.distinct()).all()

        for date in dates:
            date_str = str(date[0])  # преобразование даты в строку
            butt = 'date:' + date_str
            button = types.InlineKeyboardButton(date_str, callback_data=butt)
            markup.add(button)

        bot.send_message(call.chat.id, 'Выберите день:', reply_markup=markup)

    if call.text == 'Отменить запись':
        records = session.query(Record.date, Record.service).filter_by(visitor_id=str(call.chat.id)).all()

        markup = types.InlineKeyboardMarkup()

        for date, service in records:
            date_str = str(date)
            butt = 'date_serv:' + date_str + ':' + service
            name_butt = date_str + ' ' + service
            button = types.InlineKeyboardButton(name_butt, callback_data=butt)
            markup.add(button)

        bot.send_message(call.chat.id, 'Какую услугу хотите отменить?', reply_markup=markup)

    if call.text == 'Прайс':
        photo = open('price.jpg', 'rb')
        bot.send_photo(call.chat.id, photo, caption='Вот наш прайс:')
    if call.text == 'Перейти на сайт':
        bot.send_message(call.chat.id, 'https://nataxtare.github.io/sweet_lemon_site/')


@bot.callback_query_handler(func=lambda callback: 'date_serv:' in callback.data)
def callback_cancel(callback):

    date_serv = callback.data.split(':')
    date = date_serv[1]
    service = date_serv[2]
    master = session.query(Record.master).filter(Record.date == date, Record.service == service).first()
    master = ''.join(master)

    session.query(Record).filter(Record.date == date, Record.service == service, Record.master == master).update(
        {"visitor_id": None})
    session.commit()

    bot.send_message(callback.message.chat.id, f'Запись на {date}, "{service}" успешно отменена.')
    print(session.query(Record).all())


@bot.callback_query_handler(func=lambda callback: 'date:' in callback.data)
def callback_dates_show(callback):
    markup = types.InlineKeyboardMarkup()
    date = callback.data.split(':')[1]
    rasp_list = record_show(date)
    rasp_str = f'Информация об услугах на {date}:\n\n'

    for string in rasp_list:
        rasp_str += string
        rasp_str += '\n'
    rasp_str += '\nВыберите услугу, на которую хотели бы записаться:'


    for i in rasp_list:
        service = i.split(':')[0][1:].split(',')[0]
        reg = 'reg:' + date + ':' + service
        button = types.InlineKeyboardButton(service, callback_data=reg)
        markup.add(button)
    bot.send_message(callback.message.chat.id, rasp_str, reply_markup=markup)



@bot.callback_query_handler(func=lambda callback: 'reg:' in callback.data)
def callback_reg(callback):
    data_parts = callback.data.split(':')
    print(data_parts)
    date = data_parts[1]
    service = data_parts[2][7:]
    name = session.query(User.name).filter(User.userId == callback.message.chat.id).first()
    name = name[0]

    # Получите ID пользователя из базы данных
    user_id = session.query(User.userId).filter(User.userId == callback.message.chat.id).scalar()

    # Обновите запись, используя ID пользователя
    session.query(Record).filter(Record.service == service, Record.date == date).update({"visitor_id": user_id})


    session.commit()

    bot.send_message(callback.message.chat.id, f'Вы успешно записаны {date} на {service}')


@bot.callback_query_handler(func=lambda callback: True)
def tt(callback):
    if callback.data == 'price':
        file = open('./price.jpg', 'rb')
        bot.send_photo(callback.message.chat.id, file)

def new_name(message):

    name = message.text
    session.add(User(userId=message.chat.id, name=name))
    session.commit()
    bot.send_message(message.chat.id, 'Ваше имя успешно сохранено.')


bot.polling(none_stop=True)  # вызываем команду, благодаря которой бот работает непрерывно.
