import os, yaml, json
from lib.Core.conf import *

BASE_DIR = os.path.abspath(os.path.join(__file__, os.pardir))
CONF_ROOT = os.path.join(BASE_DIR, "conf")
MONITOR_ROOT = os.path.join(BASE_DIR, ".monitor")
USERS_ROOT = os.path.join(BASE_DIR, ".users")

def buildServerURL(port=None):
	protocol = "http"
	if SERVER_USE_SSL: protocol += "s"
	if port is None: port = SERVER_PORT
	
	return "%s://%s:%d" % (protocol, SERVER_HOST, port)

def getConfig(key):
	val = None
	with open(os.path.join(CONF_ROOT, "local.config.yaml"), 'rb') as C:
		config = yaml.load(C.read())
		try:
			val = config[key]
		except Exception as e: pass
	
		del config
	return val

def getSecrets(key, password=None):
	val = None
	with open(os.path.join(CONF_ROOT, "unveillance.secrets.json"), 'rb') as C:
		try:
			config = json.loads(C.read())
		except Exception as e:
			print "ERROR GETTING SECRET:\n%s" % e
			if password is not None:
				# TODO: might be encrypted at this point, tbd.
				print "SHOULD TRY TO DECRYPT?"
		try:
			val = config[key]
		except KeyError as e: pass
	
	del config
	return val	

with open(os.path.join(CONF_ROOT, "api.settings.yaml"), 'rb') as C:
	config = yaml.load(C.read())
	API_PORT = config['api.port']
	NUM_PROCESSES = config['api.num_processes']
	DEBUG = config['flags.debug']
	WEB_TITLE = config['api.web.title']

with open(os.path.join(CONF_ROOT, "unveillance.secrets.json"), 'rb') as C:
	config = json.loads(C.read())
	
	SERVER_HOST = config['server_host']
	SERVER_PORT = config['server_port']
	SERVER_USE_SSL = config['server_use_ssl']
	UV_COOKIE_SECRET = config['web_cookie_secret']
	ANNEX_DIR = config['annex_local']
	
	del config