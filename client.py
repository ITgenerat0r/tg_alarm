import socket
import requests
import os
from sys import argv
from uuid import getnode as get_mac
from time import sleep
from includes import *
from data_split_class import LData
from controller import Controller
# from daemon import *
import subprocess



login = "lg"
passwd = "pwd"




HOST = '192.168.0.61'
PORT = 11201  
DELAY_MAIN = 1
MAX_DELAY_MAIN = 60

VERSION = "1.0"

logs = False

old_host = HOST
old_port = PORT

current_path = os.path.dirname(os.path.abspath(__file__))

def prt(text=""):
	if logs:
		print(text)


for i in argv:
	if i == "-log":
		print("Log enabled")
		logs = True
		print(f"Version {VERSION}")
		print("Current path:", current_path)



# def req(cmnd):
# 	try:
# 		with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
# 			s.connect((HOST, PORT))
# 			cn = Controller(connection=s, logs=False)
# 			cn.send(cmnd)
# 			return cn.recv()
# 	except Exception as e:
# 		self.__prt(f"{red_text('Request failed: ')} {e}")
# 		return f"Request failed:  {e}"


help_list = ['drop', 'test', 'info']


last_rc = ""

sc = Security()


bot_running = True
while bot_running:
	# sleep(10)
	# PARSING
	data = "some parsed data"

	# connecting
	# rc = req('ns')


	# for next update use loop 
	# for lg, pwd in auth:
	login = "lg"
	passwd = "pwd"
	try:
		with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
			s.connect((HOST, PORT))
			cn = Controller(connection=s, logs=False)

			cn.send('ns')
			rx = cn.recv()
			rx_data = LData(rx)
			session_id = rx_data.get(0)
			pubkey = rx_data.get(1)

			iv = sc.new_iv()
			sha256 = sc.sha256(passwd)
			tx_data = f"{login} {iv} {sha256}"
			tx = sc.ecies_encrypt(pubkey, tx_data)
			cn.send(f"{session_id} {tx}")


			rx_en = cn.recv()
			rx = sc.decrypt(rx_en, sha256, iv)
			rx_data = LData(rx)
			if rx_data.get(0) == "success":
				# send data
				prt("Authentication was successful!")
				tx = sc.encrypt(data, sha256, rx_en[-32:])
				iv = tx[-32:]
				cn.send(f"{session_id} {tx}")

				rx_en = cn.recv()
				rx = sc.decrypt(rx_en, sha256, iv)
				if rx == "ok":
					prt("Data sended!")
					# good, data sended
			else:
				prt("Authentication failed!")






	except Exception as e:
		self.__prt(f"{red_text('Request failed: ')} {e}")

	

	DELAY_MAIN = 1
