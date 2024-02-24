import telebot
import sqlite3
import re

#token
bot = telebot.TeleBot()


name = ''
password = ''

#start message
@bot.message_handler(commands=['start'])
def main(message):
    bot.send_message(message.chat.id, 'Привет! Вот что я умею:\n/create - создать пользователя\n/login - войти в свой аккаунт')

#creating user
@bot.message_handler(commands=['create'])
def create(message):
    conn = sqlite3.connect('users.sql')
    cur = conn.cursor()
    cur.execute(
        'CREATE TABLE IF NOT EXISTS users (id int auto_increment primary key, name varchar(50), pass varchar(50), mail varchar(50))')
    conn.commit()
    cur.close()
    conn.close()
    bot.send_message(message.chat.id, 'Введите ваше имя')
    bot.register_next_step_handler(message, user_name)

def user_name(message):
    global name
    name = message.text.strip()
    if re.match('[A-Za-zа-яА-я]', name):
        conn = sqlite3.connect('users.sql')
        cur = conn.cursor()
        cur.execute(
            "SELECT name FROM users WHERE name = '%s'" % name)
        data = cur.fetchone()
        if data is None:
            bot.send_message(message.chat.id, 'Придумайте пароль')
            bot.register_next_step_handler(message, user_pass)
        else:
            bot.send_message(message.chat.id, 'Такой пользователь уже существует! Попробуйте ещё раз')
            bot.register_next_step_handler(message, user_name)
        cur.close()
        conn.close()
    else:
        bot.send_message(message.chat.id, 'Имя пользователя не должно содержать цифры! Попробуйте ещё раз')
        bot.register_next_step_handler(message, user_name)

def user_pass(message):
    global password
    password = message.text.strip()
    bot.send_message(message.chat.id, 'Теперь введите вашу почту')
    bot.register_next_step_handler(message, user_mail)

def user_mail(message):
    global name, password
    conn = sqlite3.connect('users.sql')
    cur = conn.cursor()

    mail = message.text.strip()
    if re.match('[0-9A-Za-z-_]+@[A-Za-z-]+\.[A-Za-z-]', mail):
        cur.execute(
            "INSERT INTO users (name,pass,mail) VALUES ('%s','%s','%s')" % (name, password, mail))
        bot.send_message(message.chat.id, 'Поздравляю! Пользователь создан!')
        conn.commit()
        cur.close()
        conn.close()
    else:
        bot.send_message(message.chat.id, 'Это не является почтой! Попробуйте ещё раз')
        bot.register_next_step_handler(message, user_mail)

#user login
@bot.message_handler(commands=['login'])
def login(message):
    bot.send_message(message.chat.id, 'Введите имя пользователя')
    bot.register_next_step_handler(message,get_name)

def get_name(message):
    global name
    name = message.text.strip()
    bot.send_message(message.chat.id, 'Введите пароль')
    bot.register_next_step_handler(message, get_pass)

def get_pass(message):
    global name
    password = message.text.strip()
    conn = sqlite3.connect('users.sql')
    cur = conn.cursor()
    cur.execute(
        "SELECT id FROM users WHERE name = '%s' AND pass = '%s'" % (name,password))
    data = cur.fetchone()
    if data is None:
        bot.send_message(message.chat.id, 'Имя и/или пароль неверны!')
    else:
        cur.execute(
            "SELECT mail FROM users WHERE name = '%s' AND pass = '%s'" % (name, password))
        data = str(cur.fetchone())
        bot.send_message(message.chat.id, f'Ваша почта:{data[2:-3]}')
    cur.close()
    conn.close()

#polling
bot.polling(none_stop=True)