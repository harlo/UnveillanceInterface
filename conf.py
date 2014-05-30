import os, yaml, json

BASE_DIR = os.path.abspath(os.path.join(__file__, os.pardir))
CONF_ROOT = os.path.join(BASE_DIR, "conf")

MONITOR_ROOT = os.path.join(BASE_DIR, ".monitor")

def buildServerURL(port=None):
	protocol = "http"
	if SERVER_USE_SSL: protocol += "s"
	if port is None: port = SERVER_PORT
	
	return "%s://%s:%d" % (protocol, SERVER_HOST, port)

def buildRemoteURL():
	protocol = "http"
	if SERVER_USE_SSL: protocol += "s"
	
	try:
		return "%s://%s:%d" % (protocol, SERVER_HOST, getConfig("unveillance.local_remote.api_port"))
	except Exception as e: 
		if DEBUG: print e
	return None

def getConfig(key):
	with open(os.path.join(CONF_ROOT, "local.config.yaml"), 'rb') as C:
		config = yaml.load(C.read())
		try:
			return config[key]
		except Exception as e: raise e

def getSecrets(secret_path, password=None, key=None):
	try:
		with open(secret_path, 'rb') as C:
			try:
				config = json.loads(C.read())
			except TypeError as e:
				if password is None: return None
			except ValueError as e:
				if DEBUG: print "NO SECRETS YET (VALUE ERROR?)\n%s" % e
				return None
				
				# decrypt with password
			
	except IOError as e:
		if DEBUG: print "NO SECRETS YET (IO ERROR?)\n%s" % e
		return None
	
	if key is None: return config
	
	try:
		return config[key]
	except KeyError as e:
		if DEBUG: print "could not find %s in config" % key
		return None

def saveSecret(key, secret, secret_path=None, password=None):
	if secret_path is None:
		try:
			secret_path = SECRET_PATH
		except NameError as e:
			print e
			return False
			
	secrets = getSecrets(password=password)
	if secrets is None: secrets = {}
	
	try:
		secrets[key].update(secret)
	except Exception as e:
		return False
	
	try:
		with open(os.path.join(INFORMA_CONF_ROOT, "informacam.secrets.json"), 'wb+') as C:
			C.write(json.dumps(secrets))
			return True
	except Exception as e:
		if DEBUG: print "Cannot save secret: %s" % e
	
	return False

with open(os.path.join(CONF_ROOT, "api.settings.yaml"), 'rb') as C:
	config = yaml.load(C.read())
	API_PORT = config['api.port']
	NUM_PROCESSES = config['api.num_processes']
	DEBUG = config['flags.debug']
	WEB_TITLE = config['api.web.title']

with open(os.path.join(CONF_ROOT, "local.config.yaml"), 'rb') as C:
	config = yaml.load(C.read())
	SSH_ROOT = config['ssh_root']
	SERVER_HOST = config['server.host']
	SERVER_PORT = config['server.port']
	SERVER_USE_SSL = config['server.use_ssl']
	
	try:
		UV_COOKIE_SECRET = config['api.web.cookie_secret']
		ANNEX_DIR = config['unveillance.local_remote.folder']
	except Exception as e: pass