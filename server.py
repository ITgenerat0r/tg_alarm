import socket
import os
from sys import argv
from time import sleep
import subprocess
from subprocess import PIPE
import telebot



from includes import *
from controller import Controller
from security import Security
from thread import Threads
from data_split_class import LData
from MDataBase import Alarm_database
import Config

version = "1.4"

HOST = '0.0.0.0'  # Standard loopback interface address (localhost)
PORT = 11201      # Port to listen on (non-privileged ports are > 1023)

token = Config.MyToken


logs = True

def prt(text=""):
	if logs:
		print(text)


last_arg = ""

for i in argv:
	if i[0] == '-':
		last_arg = i
		if i == "-log":
			try:
				os.system('cls')
				os.system('clear')
			except Exception as e:
				pass
			print("Log enabled")
			logs = True
			print(f"Version {version}")
	else:
		if last_arg == "-port":
			PORT = i


#define
GOOD_RESPONSE = b"OK"
help_list = ["test"]
DB_timeout = 2147483


ths = Threads()
db = Alarm_database(Config.host, Config.user, Config.password, Config.db_name)
sc = Security()
bot = telebot.TeleBot(token)


def db_connect():
	global db
	global DB_timeout
	db.connect()
	db.set_time_out(DB_timeout)



sleep(3)


def handler(conn, addr):
	global server_run
	global ths
	with conn:
		prt(f'Connected by {addr}')
		cn = Controller(conn, logs)

		data = cn.recv()
		if logs:
			print("Received:", data)

		if data[:2] == "ns":
			# iv = cn.get_new_iv()
			sp = LData(data)
			privkey, pubkey = sc.generate_rsa_keys(int(sp.get(1)))
			session_id = db.new_session(aes_key=privkey)
			cn.send(f"{session_id} {pubkey}")
		elif data.find(' ') >= 0:
			sp = LData(data)
			session_id = sp.get(0)
			en_data = sp.get(1)
			session = db.get_session(session_id)
			print(session)
			iv = session['aes_iv']
			aes_key = session['aes_key']
			if iv == "" or iv == None:
				rx = sc.rsa_decrypt(en_data, aes_key)
				rx_data = LData(rx)
				login = rx_data.get(0)
				iv = rx_data.get(1)
				sha256 = rx_data.get(2)
				mac = rx_data.get(3)
				nm = rx_data.get(4)
				db.set_online(mac, nm)
				res = "failed"
				if db.login(login, sha256):
					# ok
					db.make_bond(mac, login)
					db.set_login_to_session(session_id, login)
					db.set_iv(session_id, iv)
					db.set_aes_key(session_id, sha256)
					res = "success"
				else:
					# bad
					db.delete_session(session_id)
				tx = sc.encrypt(res, sha256, iv)
				db.set_iv(session_id, tx[-32:])
				cn.send(tx)
			else:
				data = sc.decrypt(en_data, aes_key, iv)
				tx_en = sc.encrypt('ok', aes_key, en_data[-32:])
				cn.send(tx_en)
				ldata = LData(data)
				db.set_iv(session_id, tx_en[-32:])
				if not ldata.get_size():
					return
				chat = session['user_id']


				# do something with data or ldata
				print(yellow_text(f"{data}"))
				s_ind = data.find(':')
				sender = "Unknown"
				if s_ind >= 0:
					sender = data[:s_ind]
					data = data[s_ind+2:].strip()
				if data != "no data":
					# prt(f"DATA(!= 'no data'): {data}")
					try:
						if chat:
							data = f"From {sender}: \n{data}"
							if len(data) < 4096:
								print("send all")
								bot.send_message(chat, data)
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
									bot.send_message(chat, tx)
					except Exception as e:
						print("Failed to send data!")
						print(f"Error: {e}")

				db.delete_session(session_id)
				

				# if ldata.get(0) == "drop":
				# 	server_run = False
				# 	cn.send('ok')
				# 	prt('RETURN')
				# 	return
				# elif ldata.get(0) == "help":
				# 	help_text = f"Server version {version}\r\n"
				# 	for row in help_list:
				# 		help_text += f"   {row}\r\n"
				# 	cn.send(help_text)
				# elif ldata.get(0) == 'lg': # login
				# 	res = db.login(ldata.get(1), ldata.get(2))
				# 	if res:
				# 		worker = db.get_worker(ldata.get(1))
				# 		cn.send(f"success {worker['w_name']}")
				# 	else:
				# 		cn.send("error")

				# elif ldata.get(0) == "test":
				# 	cn.send("test_ok")
				# else:
				# 	cn.send('ok')

		else:
			cn.send('bad')



def offline_seeker():
	DELAY_BETWEEN_CHECKING = 300
	
	while True:
		try:
			d = Alarm_database(Config.host, Config.user, Config.password, Config.db_name)
			global DB_timeout
			d.connect()
			d.set_time_out(DB_timeout)
			global bot
			for device in d.get_offline():
				mac = device['mac']
				nm = device['short_name']
				for u in d.get_bonds(mac):
					login = u['user_id']
					bot.send_message(login, f"Client [{mac}]({nm}) disconnected!")
				d.delete_online(mac)

		except Exception as e:
			prt(f"Error: {e}")
		sleep(DELAY_BETWEEN_CHECKING)



server_run = True
db_run = True
prt()
prt("Run offline_seeker()...")
try:
	ths.run(offline_seeker, ())
except Exception as e:
	prt("Failed to run offline_seeker()!")
	prt(f"Catching error: {e}")
	
while server_run:
	try:
		while db_run:
			try:
				db_connect()
				db_run = False
			except Exception as db_e:
				prt(f"DB error: {db_e}")
				sleep(10)
				db_run = True
		prt()
		prt("Listen...")
		prt()
		with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
			s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
			s.bind((HOST, PORT))
			s.listen()
			conn, addr = s.accept()
			prt("Thread.")
			ths.run(handler, (conn, addr))
	except Exception as e:
		prt(f"Err: {e}")
		db_run = True
