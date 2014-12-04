import yaml, os, json, copy, re
from base64 import b64encode, b64decode
from Crypto.Cipher import AES
from fabric.api import settings, local

from conf import CONF_ROOT, USER_ROOT, getConfig, DEBUG
from vars import USER_CREDENTIAL_PACK, UnveillanceCookie

try:
	from lib.Core.Utils.funcs import generateMD5Hash, generateSecureRandom
except Exception as e:
	if DEBUG: print e
	from lib.Frontend.lib.Core.Utils.funcs import generateMD5Hash, generateSecureRandom

def forceQuitUnveillance(target=None):
	if target is None:
		target = "unveillance_frontend"

	with settings(warn_only=True):
		kill_list = local("ps -ef | grep %s.py" % target, capture=True)

		for k in [k.strip() for k in kill_list.splitlines()]:
			print k

			if re.match(r".*\d{1,2}:\d{2}[:|\.]\d{2}\s+/bin/(?:ba)?sh", k) is not None: continue
			if re.match(r".*\d{1,2}:\d{2}[:|\.]\d{2}\s+grep", k) is not None: continue
			if re.match(r".*\d{1,2}:\d{2}[:|\.]\d{2}\s+.*[Pp]ython\sshutdown\.py", k) is not None: continue

			pid = re.findall(re.compile("(?:\d{3,4}|[a-zA-Z0-9_\-\+]{1,8})\s+(\d{2,6})\s+\d{1,6}.*%s\.py" % target), k)			
			print pid

			if len(pid) == 1 and len(pid[0]) >= 1:
				try:
					pid = int(pid[0])
				except Exception as e:
					print "ERROR: %s" % e
					continue

				with settings(warn_only=True): local("kill -9 %d" % pid)

def encryptUserData(plaintext, password, iv=None, p_salt=None):
	if p_salt is not None:
		password = password + p_salt
	
	if iv is None: iv = generateSecureRandom()
	else: iv = iv.decode('hex')
	
	aes = AES.new(generateMD5Hash(content=password), AES.MODE_CBC, iv)
	ciphertext = {
		'iv' : iv.encode('hex'), 
		'data' : aes.encrypt(pad(json.dumps(plaintext))).encode('hex')
	}
	
	print ciphertext
	return b64encode(json.dumps(ciphertext))

def decryptUserData(ciphertext, password, iv=None, p_salt=None):
	try:
		ciphertext_json = json.loads(b64decode(ciphertext))
		ciphertext = ciphertext_json['data'].decode('hex')
	except Exception as e:
		if DEBUG: print e
		return None
	
	if p_salt is not None:
		password = password + p_salt
	
	try:
		if iv is None: iv = ciphertext_json['iv'].decode('hex')
		else: 
			try:
				from conf import IV
			except ImportError as e:
				if DEBUG: print e
				return None

			iv = IV.decode('hex')
	except Exception as e:
		if DEBUG: print e
		return None
	
	aes = AES.new(generateMD5Hash(content=password), AES.MODE_CBC, iv)
	user_data = json.loads(unpad(aes.decrypt(ciphertext)))
	
	if user_data['username']: return user_data
	return None

def unpad(plaintext): 
	return plaintext[plaintext.index("{"):]

def pad(plaintext):
	pad = len(plaintext) % AES.block_size
	
	if pad != 0:
		pad_from = len(plaintext) - pad
		pad_size = (pad_from + AES.block_size) - len(plaintext)
		plaintext = "".join(["*" for x in xrange(pad_size)]) + plaintext
	
	return plaintext

def createNewUser(username, password, as_admin=False):
	try:
		IV = getConfig('encryption.iv')
		SALT = getConfig('encryption.salt')
		USER_SALT = getConfig('encyption.user_salt')
	except Exception as e:
		if DEBUG: print e
		return None
		
	try:
		user_data = copy.deepcopy(USER_CREDENTIAL_PACK)
		user_data['username'] = username
		if as_admin:
			user_data['admin'] = True
			user_data['annex_key_sent'] = False
			if DEBUG: print "creating %s as admin!" % username
		
		user_root = "%s.txt" % generateMD5Hash(content=username, salt=USER_SALT)
		if os.path.exists(os.path.join(USER_ROOT, user_root)):
			if DEBUG: print "user already exists NOPE!"
			return False
		
		print user_data
		
		with open(os.path.join(USER_ROOT, user_root), 'wb+') as user:
			user.write(encryptUserData(user_data, password, p_salt=SALT, iv=IV))
			return True

	except Exception as e: print e		
	return False