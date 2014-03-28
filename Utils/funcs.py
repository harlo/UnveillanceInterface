import yaml, os

from conf import CONF_ROOT

def updateConfig(new_values):
	with open(os.path.join(CONF_ROOT, "local.config.yaml"), 'rb') as C:
		config = yaml.load(C.read())
	
	config.update(new_values)

	with open(os.path.join(CONF_ROOT, "local.config.yaml"), 'wb+') as C:
		C.write(yaml.dump(config))