import telebot
from telebot import types
import sys

from threads import Threads
from process import Process
from includes import *

version = "1.0"

DB_timeout = 2147483
max_lives = 5000
max_delay_between_errors = 60
delay_between_errors = 1

prod = False

logs = False

for i in sys.argv:
	if i == "-log":
		logs = True
		print('Logs enabled!')
		print(operating_system)
	elif i == "-prod":
		prod = True

start_time = datetime.datetime.now()
last_err_time = start_time
bot = telebot.TeleBot(tk)
thr = Threads()


last_err = ""

live_countdown = max_lives

def start_bot():
	try:
		global last_err_time
		if logs:
			print(yellow_text(get_time()), "Starting...")
		last_err_time = datetime.datetime.now()
		send_info()
		if logs:
			print(yellow_text(get_time()), "Runned.")
		bot.polling(none_stop=True, timeout=100)
	except Exception as e:
		global last_err
		global delay_between_errors
		global max_delay_between_errors
		if logs:
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
	if logs:
		print(yellow_text(get_time()), f"drop {message.from_user.id} ({green_text(str(message.from_user.username))})")

	if message.from_user.id == rcid:
		if message.text.lower() in ['yes', 'y'] or not prod:
			if logs:
				print(yellow_text(get_time()), f"Bot has dropped by {message.from_user.id}({green_text(str(message.from_user.username))})")
			live_countdown = 0
			bot.send_message(message.chat.id, "Bot has ruined!")
			bot.stop_polling()
			bot.stop_bot()
			os._exit(0)
		elif message.text.lower() in ['n', 'no']:
			bot.send_message(message.chat.id, "ok.")
		else:
			bot.send_message(message.chat.id, "Are you sure? (yes/no)")
			bot.register_next_step_handler(message, drop_bot)


@bot.message_handler(commands=['info'])
def info(message):
	send_info()

def send_info():
	text = "Info: \r\n"
	text += f"OS: {operating_system}\r\n"
	text += f"MAC: {hex(mac)}\r\n"
	# text += f"IP: {ip}\r\n"
	if logs:
		print(f"text: {text}")
	bot.send_message(rcid, text)


@bot.message_handler(commands=['reset'])
def reset_live_countdown():
	global live_countdown
	global max_lives
	# bot = telebot.TeleBot(Config.MyToken)
	live_countdown = max_lives

@bot.message_handler(commands=['help'])
def help(message):
	if message.chat.id == rcid:
		text = f"Version {version}\r\n"
		bot.send_message(rcid, text)

@bot.message_handler(commands=['status'])
def get_drop_status(message):
	if message.from_user.id == rcid:
		if logs:
			print(yellow_text(get_time()), f"STATUS {message.from_user.id} ({green_text(str(message.from_user.username))})")
		text = f"live_countdown: <{live_countdown}>\r\nlen(menu_position) - {len(menu_position)}"
		if logs:
			print(text)
		bot.send_message(message.chat.id, text)

@bot.message_handler(commands=['log'])
def enable_log(message):
	if message.from_user.id == rcid:
		if message.text[5] == "1":
			logs = True
			print("Log enabled.")
		else:
			print("Log disabled.")
			logs = False



@bot.message_handler(commands=['start'])
def main(message):
	#bot.send_message(message.chat.id, '<b>Привет!</b>', parse_mode='html')
	if logs:
		try:
			print(yellow_text(get_time()), f"{message.from_user.id}({green_text(str(message.from_user.username))}): '{message.text}'")
		except Exception as e:
			print(f"start({message.text})")
	bot.send_message(message.chat.id, "Кто это?")
	bot.send_message(rcid, f"{get_time()}, {message.from_user.id}({str(message.from_user.username)}) {message.from_user.first_name} {message.from_user.last_name}: {message.text}")



@bot.message_handler(content_types='text')
def navigation(message):
	global main_menu_id
	global menu_position
	if message.text == None:
		if logs:
			print(red_text("message.text == None"))
		return
	if len(message.text) > 100:
		bot.send_message(message.chat.id, "Слишком длинное сообщение!")
		return
	if logs:
		try:
			print(yellow_text(get_time()), f"{message.from_user.id}({green_text(str(message.from_user.username))}): '{message.text}'")
		except Exception as e:
			print(f"navigation({message.text})")
	text = "возможные команды:\n"
	text += "/id - Получить логин."
	bot.send_message(message.chat.id, text)

	

while True:
	if logs:
		print()
		print(f"<<<{red_text(str(live_countdown))}>>>")
	start_bot()
	if live_countdown < 1:
		break
	if logs:
		print(f"Sleep {delay_between_errors}s")
	sleep(delay_between_errors)
	live_countdown -= 1

if logs:
	print(yellow_text(get_time()), "END")