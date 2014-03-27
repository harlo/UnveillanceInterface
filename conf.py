import os, yaml

BASE_DIR = os.path.abspath(os.path.join(__file__, os.pardir))
CONF_ROOT = os.path.join(BASE_DIR, "conf")

MONITOR_ROOT = os.path.join(BASE_DIR, ".monitor")

with open(os.path.join(BASE_DIR, "api.settings.yaml"), 'rb') as C:
	config = yaml.load(C.read())
	API_PORT = config['api_port']
	NUM_PROCESSES = config['num_processes']

with open(os.path.join(BASE_DIR, "local.config.yaml"), 'rb') as C:
	config = yaml.load(C.read())
	SSH_ROOT = config['ssh_root']