import socket
import os
from sys import argv
from time import sleep
import subprocess
from subprocess import PIPE
import telebot
import getpass



from includes import *
from controller import Controller
from security import Security
from thread import Threads
from data_split_class import LData
from MDataBase import Alarm_database


version = "1.4"

HOST = '0.0.0.0'  # Standard loopback interface address (localhost)
PORT = 24115	  # Port to listen on (non-privileged ports are > 1023)

RSA_KEY_LENGTH = 2048


token = ""
DB_HOST = "127.0.0.1"
DB_USER = ""
DB_PASS = ""
DB_NAME = "alarm_db"

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
		elif i == "-help":
			print("In development.")
			sys.exit()
	else:
		if last_arg == "-port":
			PORT = int(i)
		elif last_arg == "-rsa-length":
			try:
				if int(i) in {2048, 3072, 4096}:
					RSA_KEY_LENGTH = int(i)
			except Exception as e:
				prt(e)
		elif last_arg == "-token":
			token = i
		elif last_arg == "-dbhost":
			DB_HOST = i
		elif last_arg == "-dbuser":
			DB_USER = i
		elif last_arg == "-dbpass":
			DB_PASS = i
		elif last_arg == "-dbname":
			DB_NAME = i



# checking params
if not DB_USER:
	DB_USER = input("Enter user login for database: ")
if not DB_PASS:
	DB_PASS = getpass.getpass(f"Password for {DB_USER}: ")
if not token:
	token = input("Enter token:")



print('rsa key len', RSA_KEY_LENGTH)


#define
GOOD_RESPONSE = b"OK"
help_list = ["test"]
DB_timeout = 2147483


ths = Threads()
# db = Alarm_database(DB_HOST, DB_USER, DB_PASS, DB_NAME)
sc = Security()
bot = telebot.TeleBot(token)

privkey, pubkey = sc.generate_rsa_keys(RSA_KEY_LENGTH)

def db_connect():
	global db
	global DB_timeout
	# db.connect()
	db.selfcheck()
	db.set_time_out(DB_timeout)



sleep(3)

debug_storage = {}


def handler(conn, addr):
	global server_run
	global ths
	with conn:
		prt(f'Connected by {addr}')
		cn = Controller(conn, logs)

		db = Alarm_database(DB_HOST, DB_USER, DB_PASS, DB_NAME)
		# db.connect()
		db.selfcheck()
		data = cn.recv()
		if logs:
			print("Received:", data)

		if data[:2] == "ns":
			# iv = cn.get_new_iv()
			sp = LData(data)
			# privkey, pubkey = sc.generate_rsa_keys(int(sp.get(1)))
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
				rx = db.set_online(mac, nm)
				if rx == 1:
					# new connection
					bot.send_message(login, f"Client [{mac}]({nm}) connected!")
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



def offline_seeker(rn = True):
	DELAY_BETWEEN_CHECKING = 300
	
	while rn:
		try:
			d = Alarm_database(DB_HOST, DB_USER, DB_PASS, DB_NAME)
			d.set_logs(False)
			global DB_timeout
			# d.connect()
			d.selfcheck()
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


# def debug_offline_seeeker():
# 	DELAY_BETWEEN_CHECKING = 300
	
# 	while True:
# 		try:
			

# 		except Exception as e:
# 			prt(f"Error: {e}")
# 		sleep(DELAY_BETWEEN_CHECKING)


server_run = True
db_run = True
prt()
prt("Run offline_seeker()...")
try:
	ths.run(offline_seeker, ())
	# ths.run(debug_offline_seeeker, ())
except Exception as e:
	prt("Failed to run offline_seeker()!")
	prt(f"Catching error: {e}")
	
while server_run:
	try:
		# while db_run:
		# 	try:
		# 		db_connect()
		# 		db_run = False
		# 	except Exception as db_e:
		# 		prt(f"DB error: {db_e}")
		# 		sleep(10)
		# 		db_run = True
		prt()
		prt("Listen...")
		prt()
		with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
			s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
			s.bind((HOST, PORT))
			# for linux
			# sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
			# sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPIDLE, after_idle_sec) # 1
			# sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPINTVL, interval_sec) # 3
			# sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPCNT, max_fails) # 5
			s.listen()
			conn, addr = s.accept()
			prt("Thread.")
			ths.run(handler, (conn, addr))
	except Exception as e:
		prt(f"Err: {e}")
		db_run = True
