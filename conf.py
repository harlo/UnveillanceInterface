import os, yaml

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
		return "%s://%s:%d" % (protocol, SERVER_HOST, getConfig("unveillance.local_remote.port"))
	except Exception as e: 
		if DEBUG: print e
	return None

def getConfig(key):
	with open(os.path.join(CONF_ROOT, "local.config.yaml"), 'rb') as C:
		config = yaml.load(C.read())
		try:
			return config[key]
		except Exception as e: raise e

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
	UV_COOKIE_SECRET = config['api.web.cookie_secret']
	try:
		ANNEX_DIR = config['unveillance.local_remote.folder']
	except Exception as e: 
		if DEBUG: print e