import base64
import hashlib
# pip install pycryptodome
from Crypto.Cipher import AES
from Crypto import Random


# ECIES
import ecies



BLOCK_SIZE = 16


class Security():
	def __init__(self, log=False):
		self.__logs = log
		self.__aes_key = "develop"


	def enable_log(self, log=True):
		self.__logs = log


	def bytes2hexstr(self, data):
		return f"{data.hex()}"

	def hexstr2bytes(self, data):
		return b'' + bytes.fromhex(data)

	def new_iv(self):
		return self.bytes2hexstr(Random.new().read(AES.block_size))



	def __pad(self, s):
		# print(f"len(s) = {len(s)}")
		# print(f"+++ {(BLOCK_SIZE - len(s) % BLOCK_SIZE)} +++")
		# print(f"+++{chr(BLOCK_SIZE - len(s) % BLOCK_SIZE)}+++")
		# l = (BLOCK_SIZE - len(s) % BLOCK_SIZE) -1
		# return s + l * '0' + hex(l)[2:]

		return s + ((BLOCK_SIZE - len(s) % BLOCK_SIZE) * chr(BLOCK_SIZE - len(s) % BLOCK_SIZE)).encode('utf-8')


	def __unpad(self, s):
		# l = int(s[len(s) - 1:], 16) + 1
		# print(f"L: {l}")

		# return s[: -int(s[len(s) - 1:], 16)-1]

		return s[: -ord(s[len(s) - 1 :])]


	def encrypt(self, plain_text, key, iv):
		if self.__logs:
			print("ENCRYPT")
			print("----------------------------")
			print(f"plain_text({len(plain_text)}): '{plain_text}'")
			print("----------------------------")
			print(f"key({len(key)}): {key}")
			print(f"iv({len(iv)}): {iv}")
		# private_key = hashlib.sha256(key.encode("utf-8")).digest()
		# plain_text = self.__pad(plain_text)
		if self.__logs:
			print("----------------------------")
			print(f"padded plain_text({len(plain_text)}): '{plain_text}'")
			print("----------------------------")
		cipher = AES.new(self.hexstr2bytes(key), AES.MODE_CBC, self.hexstr2bytes(iv))
		p_text = self.__pad(plain_text.encode('utf-8'))

		print(f"p_text({len(p_text)})")
		enc_data = cipher.encrypt(p_text)
		return self.bytes2hexstr(enc_data)


	def decrypt(self, data, key, iv):
		if self.__logs:
			print("DECRYPT")
			print(f"data: {data}")
			print(f"key: {key}")
			print(f"iv: {iv}")
		cipher_text = self.hexstr2bytes(data)
		# private_key = hashlib.sha256(key.encode("utf-8")).digest()
		# private_key = self.hexstr2bytes(key)
		cipher = AES.new(self.hexstr2bytes(key), AES.MODE_CBC, self.hexstr2bytes(iv))
		return bytes.decode(self.__unpad(cipher.decrypt(cipher_text)))


	def sha256(self, data):
		return self.bytes2hexstr(hashlib.sha256(data.encode("utf-8")).digest())







	# ECIES
	def generate_ecies_key(self):
		priv_key = ecies.utils.generate_eth_key()
		priv_key_hex = priv_key.to_hex()
		pub_key_hex = priv_key.public_key.to_hex()
		return priv_key_hex, pub_key_hex

	def ecies_encrypt(self, key, data):
		return self.bytes2hexstr(ecies.encrypt(key, data.encode('utf-8')))


	def ecies_decrypt(self, key, data):
		return ecies.decrypt(key, self.hexstr2bytes(data)).decode('utf-8')

	# -----



# ------ TEST ---------------------------------------

# cl = Security()
# print(cl.sha256('test'))

# from Crypto.PublicKey import ECC

# mykey = ECC.generate(curve='p521')
# print(mykey)
# print()



# # private_data = mykey.export_key(format='DER', passphrase="pwd", protection='PBKDF2WithHMAC-SHA512AndAES256-CBC', prot_params={'iteration_count':131072})
# private_data = mykey.export_key(format='DER')
# print(cl.bytes2hexstr(private_data))
# print()



# public_data = mykey.public_key().export_key(format='DER')
# print(cl.bytes2hexstr(public_data))





# ECC

# cl = Security()
# privKeyHex, pubKeyHex = cl.generate_ecies_key()


# print("Encryption public key:", pubKeyHex)
# print("Decryption private key:", privKeyHex)
# print()

# plaintext = 'Some plaintext for encryption'
# print("Plaintext:", plaintext)
# print()

# encrypted = cl.ecies_encrypt(pubKeyHex, plaintext)
# # print("Encrypted:", binascii.hexlify(encrypted))
# print("Encrypted:", encrypted)
# print()

# decrypted = cl.ecies_decrypt(privKeyHex, encrypted)
# print("Decrypted:", decrypted)








# AES

# cp = Security(True)
# # message = "asdfasdf-0123456789abcef0123456789abcdef"
# message = "DATA: default: 1235215ffasdfasdfп"
# # message = input("->")
# key = cp.sha256("develop")
# # iv = "c33bfeae1263c98633bc9e66c6ab8746"
# iv = cp.new_iv()

# print(f"Init text({len(message)}): ", message)
# encrypted_msg = cp.encrypt(message, key, iv)
# print(f"Encrypted Message({len(encrypted_msg)}):", encrypted_msg)
# decrypted_msg = cp.decrypt(encrypted_msg, key, iv)
# print("Decrypted Message:", decrypted_msg)

# ---------------------------------------------------