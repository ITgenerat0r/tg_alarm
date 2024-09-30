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
from parser import Parser
# from daemon import *
# import subprocess
import getpass

help_data = "client -u <login> -name <name(who sended data)> -f <input_file> -ip <ip> -port <port>"

users = {}

filename = "test.txt"
station_name = "default"



HOST = '192.168.0.161'
PORT = 11201  
DELAY_MAIN = 1
MAX_DELAY_MAIN = 60
RSA_KEY_LENGTH = 2048

VERSION = "1.1"

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
			pwd = getpass.getpass(f"Password for user {i}: ")
			users[i] = pwd
		elif last_arg == "-f":
			filename = i
		elif last_arg == "-ip":
			HOST = i
		elif last_arg == "-port":
			PORT = i
		elif last_arg == "-name":
			station_name = i


	
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

sc = Security(True)
p = Parser()


bot_running = True
while bot_running:
	# PARSING
	# data = f"{station_name}: \n"
	data = p.parse_file(filename)



	prt(yellow_text(f"DATA: {data}"))
	# connecting
	# rc = req('ns')


	if data:
		for login in users:
			passwd = users[login]

			rx = req(f'ns {RSA_KEY_LENGTH}')
			sc.set_key_len(RSA_KEY_LENGTH)

			rx_data = LData(rx)
			session_id = rx_data.get(0)
			pubkey = rx_data.get(1)

			iv = sc.new_iv()
			sha256 = sc.sha256(passwd)
			tx_data = f"{login} {iv} {sha256}"
			tx = sc.rsa_encrypt(tx_data, pubkey)

			rx_en = req(f"{session_id} {tx}")

			rx = sc.decrypt(rx_en, sha256, iv)
			rx_data = LData(rx)
			if rx_data.get(0) == "success":
				# send data
				prt(f"Authentication was successful ({login})!")
				tx = sc.encrypt(f"{station_name}: \n{data}", sha256, rx_en[-32:])
				iv = tx[-32:]

				rx_en = req(f"{session_id} {tx}")

				rx = sc.decrypt(rx_en, sha256, iv)
				if rx == "ok":
					prt(f"Data sended ({login})!")
					# good, data sended
			else:
				prt(f"Authentication failed ({login})!")



	sleep(10)
	# bot_running = False # dev, remove for release
	DELAY_MAIN = 1


