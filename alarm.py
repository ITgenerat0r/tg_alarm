import socket
# import requests
import os
import sys
from sys import argv
from time import sleep
from includes import *
from data_split_class import LData
from controller import Controller
from security import Security
from parser_class import Parser
# from daemon import *
# import subprocess
import getpass


from thread import Threads
import telebot

from uuid import getnode as get_mac

help_data = "client.exe -token <bot_token> -u <login1> <login2>\n\
 Additional: -name <name(who sended data)> -f <input_file>"

# users = {}
users = []
token = ""

filename = "logs.txt"
config_filename = "../wellinfo.config"
station_name = "default"



# HOST = '192.168.0.161'
HOST = '192.168.0.161'
PORT = 11201  
DELAY_MAIN = 60
MAX_DELAY_MAIN = 60
RSA_KEY_LENGTH = 2048
MAC = hex(get_mac())[2:]

VERSION = "1.6"

logs = True

old_host = HOST
old_port = PORT

current_path = os.path.dirname(os.path.abspath(__file__))

def prt(text=""):
	if logs:
		print(text)



last_arg = ""
for i in argv:
	if i[0] == '-':
		last_arg = i
		if i == "-log":
			print("Log enabled")
			logs = True
		elif i == "-help":
			print(f"Version {VERSION}")
			print(help_data)
			sys.exit()
	else:
		if last_arg == "-u":
			# pwd = getpass.getpass(f"Password for user {i}: ")
			users.append(i)
		elif last_arg == "-f":
			filename = i
		elif last_arg == "-ip":
			HOST = i
		elif last_arg == "-port":
			PORT = int(i)
		elif last_arg == "-name":
			station_name = i
		elif last_arg == "-token":
			token = i


if not token:
	token = input("Enter token:")
	
if logs:
	print(f"Version {VERSION}")
	print("Current path:", current_path)




def req(cmnd):
	try:
		with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
			s.connect((HOST, PORT))
			cn = Controller(connection=s, logs=False)
			cn.send(cmnd)
			return cn.recv()
	except Exception as e:
		prt(f"{red_text('Request failed: ')} {e}")
		return f"Request failed:  {e}"


help_list = ['drop', 'test', 'info']


last_rc = ""


# if station_name == "default":
# 	station_name = input("Enter station name:")


bot = telebot.TeleBot(token)
sc = Security(True)
p = Parser()
station_data = p.parse_config(config_filename)
data = f"Started at {get_time()}(local time)\n"
try:
	tx_station_data = p.translate_config(station_data)
	for i in tx_station_data:
		data += f"{i}: {tx_station_data[i]}\n"
except Exception as e:
	print(e)



def start_bot():
	try:
		bot.polling(none_stop=False, timeout=1)
	except Exception as e:
		print(f"Bot error: {e}")


def bot_live():
	while True:
		start_bot()

ths = Threads()
try:
	ths.run(bot_live, ())
	# ths.run(debug_offline_seeeker, ())
except Exception as e:
	prt("Failed to run bot_live()!")
	prt(f"Catching error: {e}")

@bot.message_handler(content_types='text')
def common(message):
	if message.text == None:
		print(red_text("message.text == None"))
		return
	if len(message.text) > 100:
		bot.send_message(message.chat.id, "Слишком длинное сообщение!")
		return
	# bot.send_message(message.chat.id, f"Сам {message.text}")
	# show help here)

	bot.send_message(message.chat.id, f"Ваш логин: {message.chat.id}")










if not users:
	print("")
	lg = input("Enter login:")
	users.append(lg)





bot_running = True
while bot_running:

	# PARSING
	# data = f"{station_name}: \n"
	data += p.parse_file(filename)


	prt(yellow_text(f"DATA: {data}"))
	# connecting
	# rc = req('ns')

	# if not data:
	# 	data = "no data"

	if data:
		for login in users:
			try:
				if len(data) < 4096:
					print("send all")
					bot.send_message(login, data)
				else:
					print("send by parts")
					while len(data) > 0:
						print("len data:", len(data))
						x = 4090
						ind = data[:x].rfind('\n')
						if len(data) > 4090 and ind >= 0:
							x = ind
						tx = data[:x]
						data = data[x:]
						bot.send_message(login, tx)
			except Exception as e:
				print(f"Error: {e}")
	else:
		print("No data!")
				

	

	data = ""

	sleep(DELAY_MAIN)
	# bot_running = False # dev, remove for release


