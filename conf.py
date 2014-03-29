import os, yaml
from lib.Core.Utils.funcs import generateMD5Hash

BASE_DIR = os.path.abspath(os.path.join(__file__, os.pardir))
CONF_ROOT = os.path.join(BASE_DIR, "conf")

MONITOR_ROOT = os.path.join(BASE_DIR, ".monitor")

def getUUID():
	try:
		with open(os.path.join(SSH_ROOT, "unveillance.local_remote.key.pub"), 'rb') as PK:			
			return generateMD5Hash(content=PK.read())

	except Exception as e: print e
	return None

def getRemotePort():
	try:
		with open(os.path.join(CONF_ROOT, "local.config.yaml"), 'rb') as C:
			config = yaml.load(C.read())
			return config['unveillance.local_remote.port']
			
	except Exception as e: 
		if DEBUG: print e
	return None

def buildServerURL(port=None):
	if port is None: port = SERVER_PORT
	
	return "http://%s:%d" % (SERVER_HOST, port)

def buildRemoteURL():
	protocol = "http"
	if SERVER_USE_SSL: protocol += "s"
	
	try:
		return "%s://%s:%d" % (protocol, SERVER_HOST, REMOTE_PORT)
	except Exception as e: 
		if DEBUG: print e
	return None

with open(os.path.join(CONF_ROOT, "api.settings.yaml"), 'rb') as C:
	config = yaml.load(C.read())
	API_PORT = config['api.port']
	NUM_PROCESSES = config['api.num_processes']
	DEBUG = config['flags.debug']

with open(os.path.join(CONF_ROOT, "local.config.yaml"), 'rb') as C:
	config = yaml.load(C.read())
	SSH_ROOT = config['ssh_root']
	SERVER_HOST = config['server.host']
	SERVER_PORT = config['server.port']

UUID = getUUID()
REMOTE_PORT = getRemotePort()

if DEBUG:
	print "\nLOCAL.CONFIG.YAML:"
	
	print "\tSERVER_URL: %s" % buildServerURL()
	print "\tUUID: %s" % getUUID()
	print "\tREMOTE_PORT: %s" % getRemotePort() 
	
	print "\n"