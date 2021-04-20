from base64 import b64encode, b64decode
from hashlib import sha256
from sys import argv
from Crypto.Cipher import AES
from Crypto import Random
from os import chdir
from fileIO import writeList

BLOCK_SIZE = 16
pad = lambda s: bytes(s + (BLOCK_SIZE - len(s) % BLOCK_SIZE) * chr(BLOCK_SIZE - len(s) % BLOCK_SIZE), 'utf-8')
unpad = lambda s: s[:-ord(s[len(s) - 1:])]

#A function to encrypt a decrypted phrase
def encrypt(raw, password):
	private_key = sha256(password.encode("utf-8")).digest()
	raw = pad(raw)
	iv = Random.new().read(AES.block_size)
	cipher = AES.new(private_key, AES.MODE_CBC, iv)
	return b64encode(iv + cipher.encrypt(raw))

#A function to decrypt an encrypted phrase
def decrypt(enc, password):
	private_key = sha256(password.encode("utf-8")).digest()
	enc = b64decode(enc)
	iv = enc[:16]
	cipher = AES.new(private_key, AES.MODE_CBC, iv)
	return unpad(cipher.decrypt(enc[16:]))

if __name__ == '__main__':
	mode = argv[1].strip()[0].upper()
	file = argv[2].strip()
	password = argv[3].strip()
	content = open(file, 'r').read()
	if (mode == 'E'):
		open(file, 'w').write(str(encrypt(content, password)))
		print(f"Successfully encrypted {file}")
	elif (mode == 'D'):
		with open(file, 'w') as fObj:
			writeList(fObj, str(decrypt(pad(content[2:-1]), password))[2:-1].replace('\\n','\n').split('\n'))
		print(f"Successfully decrypted {file}")