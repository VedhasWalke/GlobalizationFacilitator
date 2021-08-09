from base64 import b64encode, b64decode
from hashlib import sha256
from sys import argv
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto import Random

BLOCK_SIZE = 16

#A function to encrypt a decrypted phrase
def encrypt(raw, password):
	private_key = sha256(password.encode("utf-8")).digest()
	raw = pad(raw, BLOCK_SIZE)
	iv = Random.new().read(AES.block_size)
	cipher = AES.new(private_key, AES.MODE_CBC, iv)
	return b64encode(iv + cipher.encrypt(raw))

#A function to decrypt an encrypted phrase
def decrypt(enc, password):
	private_key = sha256(password.encode("utf-8")).digest()
	enc = b64decode(enc)
	iv = enc[:16]
	cipher = AES.new(private_key, AES.MODE_CBC, iv)
	return unpad(cipher.decrypt(enc[16:]), BLOCK_SIZE)

if __name__ == '__main__':
	mode = argv[1].strip()[0].upper()
	file = argv[2].strip()
	password = argv[3].strip()
	content = open(file, 'rb').read()
	if (mode == 'E'):
		try:
			open(file, 'wb').write(encrypt(content, password))
			print(f"Successfully encrypted {file}")
		except:
			open(file, 'wb').write(content)
			print(f"Error encrypting {file}")
	elif (mode == 'D'):
		try:
			open(file, 'wb').write(decrypt(content, password))
			print(f"Successfully decrypted {file}")
		except:
			open(file, 'wb').write(content)
			print(f"Error decrypting {file}")
	else:
		raise ValueError("Unknown encryption/decryption method selected")