import os, yaml, json
from lib.Core.conf import *

BASE_DIR = os.path.abspath(os.path.join(__file__, os.pardir))
CONF_ROOT = os.path.join(BASE_DIR, "conf")
MONITOR_ROOT = os.path.join(BASE_DIR, ".monitor")
USER_ROOT = os.path.join(BASE_DIR, ".users")

SHA1_INDEX = True

PERMISSIONS = {
	'upload_local' : [],
	'upload_global' : []
}

def buildServerURL(port=None):
	protocol = "http"
	if SERVER_USE_SSL: protocol += "s"
	if port is None: port = SERVER_PORT
	
	server_url = "%s://%s" % (protocol, SERVER_HOST)
	
	if port in [80, 443]:
		return server_url
	else:
		return "%s:%d" % (server_url, port)

def buildTaskChannelURL(request, with_status=None):
	for p in ["host", "protocol", "remote_ip", "path"]:
		if hasattr(request, p):
			print "%s : %s" % (p, getattr(request, p))

	if with_status is not None:
		print "WITH STATUS: ", with_status

		if with_status == 0 and TASK_CHANNEL_MASK is not None:
			return TASK_CHANNEL_MASK

	return "%s://%s%s" % ( \
		request.protocol, TASK_CHANNEL_URL, \
		(":%d" % TASK_CHANNEL_PORT))

def getConfig(key):
	val = None
	try:
		with open(os.path.join(CONF_ROOT, "local.config.yaml"), 'rb') as C:
			config = yaml.load(C.read())
			try:
				val = config[key]
			except Exception as e: pass
	
			del config
	except Exception as e: pass
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
	NUM_PROCESSES = config['api.num_processes']
	DEBUG = config['flags.debug']
	WEB_TITLE = config['api.web.title']

API_PORT = getConfig('api.port')

try:
	GIT_ANNEX = os.path.join(getConfig('git_annex_dir'), "git-annex")
except Exception as e: 
	print e, type(e)
	pass

try:
	PYTHON_HOME = getConfig('python_home')
except Exception as e: pass

try:
	with open(os.path.join(CONF_ROOT, "unveillance.secrets.json"), 'rb') as C:
		config = json.loads(C.read())
	
		try:
			SERVER_HOST = config['server_host']
		except KeyError as e: pass
		
		try:
			SERVER_PORT = config['server_port']
		except KeyError as e: pass
		
		try:
			SERVER_USE_SSL = config['server_use_ssl']
		except KeyError as e: pass
		
		try:
			UV_COOKIE_SECRET = config['web_cookie_secret']
		except KeyError as e: pass
		
		try:
			ANNEX_DIR = config['annex_local']
		except KeyError as e: pass
		
		try:
			SSH_ROOT = config['ssh_root']
		except KeyError as e: pass

		try:
			protocol = "http"
			if getSecrets('server_message_port') in [443] or getSecrets('server_message_use_ssl'):
				protocol += "s"

			TASK_CHANNEL_URL = getSecrets('server_host')
			TASK_CHANNEL_PORT = getSecrets('server_message_port') if getSecrets('server_message_port') is not None else (getSecrets('server_port') + 1)
		except Exception as e:
			print "******* TASK CHANNEL ERROR ********"
			print e

		try:
			TASK_CHANNEL_MASK = getSecrets('server_task_channel_mask')
		except Exception as e:
			TASK_CHANNEL_MASK = None

		try:
			SHA1_INDEX = config['index.sha1']
		except KeyError as e:
			pass
	
		del config
except IOError as e: pass