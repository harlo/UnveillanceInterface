import os, yaml
from lib.Core.Utils.funcs import hashEntireFile

BASE_DIR = os.path.abspath(os.path.join(__file__, os.pardir))
CONF_ROOT = os.path.join(BASE_DIR, "conf")

MONITOR_ROOT = os.path.join(BASE_DIR, ".monitor")

def getUUID():
	try:
		with open(os.path.join(SSH_ROOT, "unveillance.local_remote.key.pub"), 'rb') as PK:
			return hashEntireFile(PK.read())

	except Exception as e: print e
	return None

def buildServerURL():
	protocol = "http"
	if SERVER_USE_SSL: protocol += "s"
	
	return "%s://%s:%d" % (protocol, SERVER_HOST, SERVER_PORT)

with open(os.path.join(CONF_ROOT, "api.settings.yaml"), 'rb') as C:
	config = yaml.load(C.read())
	API_PORT = config['api.port']
	NUM_PROCESSES = config['api.num_processes']
	DEBUG = config['flags.debug']

with open(os.path.join(CONF_ROOT, "local.config.yaml"), 'rb') as C:
	config = yaml.load(C.read())
	SSH_ROOT = config['ssh_root']
	SERVER_HOST = config['server.host']
	SERVER_USE_SSL = config['server.use_ssl']
	SERVER_PORT = config['server.port']
	UUID = getUUID()

if DEBUG:
	print "SERVER_URL: %s" % buildServerURL()
	print "UUID: %s" % getUUID()