import socket
import requests
import os
from sys import argv
from uuid import getnode as get_mac
from time import sleep
from includes import *
from data_split_class import LData
from controller import Controller
from security import Security
from parser import Parser
# from daemon import *
import subprocess
import getpass

# client -u <login> -f <input_file> -ip <ip> -port <port>

users = {}

filename = "test.txt"




HOST = '192.168.0.161'
PORT = 11201  
DELAY_MAIN = 1
MAX_DELAY_MAIN = 60

VERSION = "1.0"

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
	else:
		if last_arg == "-u":
			pwd = getpass.getpass(f"Password for user {i}: ")
			users[i] = pwd
		elif last_arg == "-f":
			filename = i
		elif last_arg == "-ip":
			HOST = i
		elif last_arg == "-port":
			PORT = i


	
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

sc = Security()
p = Parser()


bot_running = True
while bot_running:
	# sleep(10)
	# PARSING
	data = p.parse_file(filename)
	# data = "some parsed data"



	prt(yellow_text(f"DATA: {data}"))
	# connecting
	# rc = req('ns')


	
	for login in users:
		passwd = users[login]

		rx = req('ns')

		rx_data = LData(rx)
		session_id = rx_data.get(0)
		pubkey = rx_data.get(1)

		iv = sc.new_iv()
		sha256 = sc.sha256(passwd)
		tx_data = f"{login} {iv} {sha256}"
		tx = sc.ecies_encrypt(pubkey, tx_data)

		rx_en = req(f"{session_id} {tx}")

		rx = sc.decrypt(rx_en, sha256, iv)
		rx_data = LData(rx)
		if rx_data.get(0) == "success":
			# send data
			prt(f"Authentication was successful ({login})!")
			tx = sc.encrypt(data, sha256, rx_en[-32:])
			iv = tx[-32:]

			rx_en = req(f"{session_id} {tx}")

			rx = sc.decrypt(rx_en, sha256, iv)
			if rx == "ok":
				prt(f"Data sended ({login})!")
				# good, data sended
		else:
			prt(f"Authentication failed ({login})!")


	bot_running = False # dev, remove for release
	DELAY_MAIN = 1


