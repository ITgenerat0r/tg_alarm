import os
from includes import green_text, yellow_text, red_text, blue_text
from security import Security


# for exchange between client and server
class Controller():
	"""docstring for Controller"""
	def __init__(self, connection, logs = False):
		self.__connection = connection
		self.__logs = logs
		self.__package_size = 1024
		self.__code_size = 2
		self.__cipher = Security(self.__logs)
		self.__encryption = False
		self.__iv = ""
		self.__aes_key = "develop"

	def enable_encryption(self, stat=True):
		self.__encryption = stat


	def set_iv(self, iv):
		self.__iv = iv

	def get_iv(self):
		return self.__iv


	def get_new_iv(self):
		return self.__cipher.new_iv()

	



	def __prt(self, text=""):
		if self.__logs:
			print(text)

	def __send_bit(self, text):
		self.__connection.sendall(text.encode('utf-8'))
		self.__prt(blue_text(f" => {text}"))

	def __recv_bit(self):
		res = self.__connection.recv(self.__package_size).decode('utf-8')
		self.__prt(blue_text(f" <= {str(res)}"))
		return res

	def send(self, text):
		# self.__prt(f"send({text})")
		# text = self.__cipher.encrypt(text_clear)
		if self.__encryption:
			text = self.encrypt(text)
			self.__iv = text[-32:]
		self.__prt()
		while len(text) > self.__package_size - self.__code_size:
			self.__send_bit(f"b_{text[:self.__code_size]}")
			text = text[self.__code_size:]
			self.__recv_bit()
		else:
			self.__send_bit(f"e_{text}")

	def recv(self):
		# dt = self.__recv_bit()
		# res = dt[self.__code_size:]
		self.__prt()
		res = ""
		while True:
			dt = self.__recv_bit()
			res += dt[self.__code_size:]
			if dt[:self.__code_size] == 'b_':
				self.__send_bit('ok')
			else:
				break
		# self.__prt(f"recv() = {res}")
		if self.__encryption:
			return self.decrypt(res)
		return res

	def decrypt(self, data):
		return self.__cipher.decrypt(data, self.__aes_key, self.__iv)

	def encrypt(self, data):
		return self.__cipher.encrypt(data, self.__aes_key, self.__iv)


	# it's returned: privKey, pubKey
	def get_new_ecc_keys(self):
		return self.__cipher.generate_ecies_key()

	def ecc_decrypt(self, key, data):
		return self.__cipher.ecies_decrypt(key, data)

	def ecc_encrypt(self, key, data):
		return self.__cipher.ecies_encrypt(key, data)


