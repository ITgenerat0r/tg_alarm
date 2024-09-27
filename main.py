import telebot
from telebot import types
from threads import Threads

from includes import *
import Config
import sys
from MDataBase import Alarm_database
from security import Security


# DB = MDataBase.Database("localhost", "root", Config.password, Config.bd_name)
# DB = MDataBase.DatabaseTS("localhost", "root", Config.password, Config.bd_name_ts)


# admins
admins = Config.admins


DB_timeout = 2147483
max_lives = 5000
max_delay_between_errors = 60
delay_between_errors = 1

token = Config.MyToken

prod = True


start_time = datetime.datetime.now()
last_err_time = start_time

print('bot init...')
bot = telebot.TeleBot(token)
print('threads init...')
thr = Threads()

db = Alarm_database(Config.host, Config.user, Config.password, Config.db_name)

update_state = True

black_list = []
is_sending = []

last_err = ""

live_countdown = max_lives

def start_bot():
    try:
        global last_err_time
        print(yellow_text(get_time()), "Starting...")
        last_err_time = datetime.datetime.now()
        global db
        global DB_timeout
        db.connect()
        db.set_time_out(DB_timeout)
        print(yellow_text(get_time()), "Runned.")
        bot.polling(none_stop=False, timeout=1)
    except Exception as e:
        global last_err
        global delay_between_errors
        global max_delay_between_errors
        print(yellow_text(get_time()), "Exception raised.")
        print(e)
        if str(e).find(last_err) > -1:
            if delay_between_errors < max_delay_between_errors:
                delay_between_errors += 1
        else:
            last_err = str(e)[:int(len(str(e))/3)]
            delay_between_errors = 1


@bot.message_handler(commands=['drop', 'stop'])
def drop_bot(message):

    if message.from_user.id == Config.ITGenerator:
        if message.text.lower() in ['yes', 'y'] or not prod:
            print(yellow_text(get_time()), f"Bot has dropped by {message.from_user.id}({green_text(str(message.from_user.username))})")
            live_countdown = 0
            bot.send_message(message.chat.id, "Bot has ruined!")
            bot.stop_polling()
            bot.stop_bot()
            os._exit(0)
        elif message.text.lower() in ['n', 'no']:
            bot.send_message(message.chat.id, 'ok')
        else:
            bot.send_message(message.chat.id, "Are you sure?")
            bot.register_next_step_handler(message, drop_bot)

@bot.message_handler(commands=['reborn'])
def reborn(message):

    print(yellow_text(get_time()), f"reborn {message.from_user.id} ({green_text(str(message.from_user.username))})")
    if message.from_user.id in admins:
        reset_live_countdown()
        bot.send_message(message.chat.id, "Done!")


def reset_live_countdown():
    global live_countdown
    global max_lives
    global is_sending
    # bot = telebot.TeleBot(Config.MyToken)
    # thr = Threads()
    with thr.rlock():
        is_sending = []
        live_countdown = max_lives

@bot.message_handler(commands=['status'])
def get_drop_status(message):
    print(yellow_text(get_time()), f"STATUS {message.from_user.id} ({green_text(str(message.from_user.username))})")
    if message.from_user.id in admins:
        text = f"live_countdown: <{live_countdown}>"
        print(text)
        bot.send_message(message.chat.id, text)



def parse_date_value(raw_data):
    bindex = raw_data.find('(')
    if bindex >= 0:
        eindex = raw_data[bindex:].find(')')
        if eindex >= 0:
            return raw_data[bindex+1:bindex+eindex]
    return ""

def is_number(text):
    alphabet = set({'0', '1', '2', '3', '4', '5', '6', '7', '8', '9'})
    for c in text:
        if not c in alphabet:
            return False
    return True

@bot.message_handler(commands=['send'])
def send_message_to_user(message):
    if message.from_user.id in admins:
        print(message.text)
        mdata = message.text.split()
        # for i in mdata:
        #     print(f"- {i}")
        if len(mdata) >= 3:
            user_id = mdata[1]
            beginid = message.text.find(mdata[2])
            # print(beginid)
            # print(message.text[beginid:])
            try:
                bot.send_message(user_id, message.text[beginid:])
            except Exception as e:
                print(e)


@bot.message_handler(commands=['start'])
def start(message):
    #bot.send_message(message.chat.id, '<b>Привет!</b>', parse_mode='html')
    u = db.get_user(message.chat.id)
    if u:
        common(message)
    else:
        bot.send_message(message.chat.id, f"Здравствуйте, {message.from_user.first_name} {message.from_user.last_name}!")
        get_login(message)

@bot.message_handler(commands=['get_login'])
def get_login(message):
    bot.send_message(message.chat.id, f"Ваш логин: {message.chat.id}")
    u = db.get_user(message.chat.id)
    if u:
        db.set_user_name(message.chat.id, f"{message.from_user.first_name} {message.from_user.last_name}")
    else:
        new_pass(message)


@bot.message_handler(commands=['new_pass'])
def new_pass(message):
	bot.send_message(message.chat.id, f"Придумайте новый пароль:")
	bot.register_next_step_handler(message, set_pass)

def set_pass(message):
	# set pass
    sc = Security()
    login = message.chat.id
    pwd = message.text
    sha256 = sc.sha256(pwd)
    name = f"{message.from_user.first_name} {message.from_user.last_name}"

    
    if db.get_user(message.chat.id):
        db.set_user_password(login, sha256)
        db.set_user_name(login, name)
    else:
        db.add_user(login, sha256, name)
    bot.send_message(message.chat.id, f"Done!")


@bot.message_handler(content_types='text')
def common(message):
    if message.text == None:
        print(red_text("message.text == None"))
        return
    if len(message.text) > 100:
        bot.send_message(message.chat.id, "Слишком длинное сообщение!")
        return
    bot.send_message(message.chat.id, f"Сам {message.text}")
    # show help here)
    



while True:
    print()
    print(f"<<<{red_text(str(live_countdown))}>>>")
    start_bot()
    if live_countdown < 1:
        break
    print(f"Sleep {delay_between_errors}s")
    sleep(delay_between_errors)
    live_countdown -= 1

# print(yellow_text(get_time()), "END")