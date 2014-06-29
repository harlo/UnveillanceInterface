import os, re, json
from time import time, sleep
from sys import argv, exit
from fabric.api import local, settings
from fabric.operations import prompt

from lib.Core.Utils.funcs import generateSecureNonce, generateSecureRandom, generateNonce

def locateLibrary(lib_rx):
	base_dir = os.getcwd()
	
	for _, dir, _ in os.walk(os.path.join(base_dir, "lib")):
		print dir
		for d in dir:
			if re.match(lib_rx, d) is not None:
				return os.path.join(base_dir, "lib", d)

		break
	
	return None

if __name__ == "__main__":
	base_dir = os.getcwd()
	config = {}
	
	if len(argv[1]) > 3:		
		try:
			with open(argv[1], 'rb') as CONF:
				config.update(json.loads(CONF.read()))
		except Exception as e:
			print e
	
	print "****************************"
	print "Hello.  Welcome to Unveillance Frontend setup."
	admin_username = prompt("Choose a username:")
	admin_pwd = prompt("Pick a good password:")

	print "****************************"	
	print "Google Drive Authentication:"
	print "If you want to to use Google Drive to import documents into the Annex server, you must authenticate the application by visiting the URL below."
	print "You will be shown an authentication code that you must paste into this terminal when prompted."
	print "Authenticate Google Drive? y or n"
	
	gdrive_auth = False
	if prompt("[DEFAULT: n]") == "y": gdrive_auth = True
	
	if gdrive_auth:
		from oauth2client.client import OAuth2WebServerFlow
		from oauth2client.file import Storage
		
		config.update({
			'auth_storage' : os.path.join(base_dir, "conf", "drive.secrets.json"),
			'scopes' : ["https://www.googleapis.com/auth/drive",
				"https://www.googleapis.com/auth/drive.file",
				"https://www.googleapis.com/auth/drive.install",
				"https://www.googleapis.com/auth/userinfo.profile"
			],
			'account_type' : "user",
			'redirect_url' : "urn:ietf:wg:oauth:2.0:oob"
		})
		
		if 'annex_admin_email' not in config.keys():
			print "Admin's email address?"
			config['annex_admin_email'] = prompt("[DEFAULT: none] ")
		
			if len(config['annex_admin_email']) == 0:
				config['annex_admin_email'] = None
		
		if 'client_id' not in config.keys():
			config['client_id'] = prompt("Client ID: ")
		
		if 'client_secret' not in config.keys():
			config['client_secret'] = prompt("Client Secret: ")
			
		flow = OAuth2WebServerFlow(config['client_id'], config['client_secret'],
			config['scopes'], config['redirect_url'])
		
		print "To use Google Drive to import documents into the Annex server, you must authenticate the application by visiting the URL below."
		print "You will be shown an authentication code that you must paste into this terminal when prompted."
		print "URL: %s" % flow.step1_get_authorize_url()
		credentials = flow.step2_exchange(prompt("Code: "))
		Storage(config['auth_storage']).put(credentials)
	
	if 'server_host' not in config.keys():
		print "What is the Public IP/hostname of the Annex server?"
		config['server_host'] = prompt("[DEFAULT: localhost] ")
		
		if len(config['server_host']) == 0: config['server_host'] = "127.0.0.1"
	
	if config['server_host'] != "127.0.0.1":
		if 'annex_local' not in config.keys():
			print "Where do you want your Unveillance folder?  The folder should not exist."
			config['annex_local'] = prompt("[DEFAULT: ~/unveillance_local]")
	
		if len(config['annex_local']) == 0:
			config['annex_local'] = os.path.join(os.path.expanduser("~"), "unveillance_local")

		with settings(warn_only=True):
			local("mkdir %s" % config['annex_local'])
		
		git_annex_dir = locateLibrary(r'git-annex\.*')
		if git_annex_dir is None:
			with settings(warn_only=True):
				local("wget -O lib/git-annex.tar.gz http://downloads.kitenet.net/git-annex/linux/current/git-annex-standalone-amd64.tar.gz")
				local("tar -xvzf lib/git-annex.tar.gz -C lib")
				local("rm lib/git-annex.tar.gz")
		
			git_annex_dir = locateLibrary(r'git-annex\.*')			
	
	if 'server_port' not in config.keys():
		print "What port is the Annex server on?"
		config['server_port'] = prompt("[DEFAULT: 8889] ")
	
	if type(config['server_port']) is not int:
		if len(config['server_port']) == 0: config['server_port'] = 8889
	
	if 'annex_remote' not in config.keys():
		print "What is the path to the Annex's repository?"
		config['annex_remote']  = prompt("[DEFAULT: ~/unveillance_remote]")
	
	if len(config['annex_remote']) == 0:
		if config['server_host'] == "127.0.0.1":
			config['annex_remote'] = os.path.join(os.path.expanduser("~"),
				"unveillance_remote")
		else:
			config['annex_remote'] = "~/unveillance_remote"
	
	if config['server_host'] == "127.0.0.1": 
		config['server_use_ssl'] = False
		config['annex_local'] = config['annex_remote']
	else:
		if 'ssh_root' not in config.keys():
			print "Where is your ssh folder?"
			config['ssh_root'] = prompt("[DEFAULT: ~/.ssh] ")
		
		if len(config['ssh_root']) == 0:
			config['ssh_root'] = os.path.join(os.path.expanduser("~"), ".ssh")

		print "Unveillance will now generate a public/private key pair for communication with the server"
		config['ssh_key_pwd'] = generateNonce(top_range=59, bottom_range=29)
		config['ssh_key_priv'] = os.path.join(config['ssh_root'],
			"unveillance.%d.key" % time())
		config['ssh_key_pub'] = "%s.pub" % config['ssh_key_priv']
	
		with settings(warn_only=True):
			local("ssh-keygen -f %s -t rsa -b 4096 -N %s" % (config['ssh_key_priv'],
				config['ssh_key_pwd']))
		
		if 'server_user' not in config.keys():
			config['server_user'] = prompt("What user name should SSH use? : ")
		
		if 'annex_remote_port' not in config.keys():
			print "What port does the Annex server SSH to?"
			config['annex_remote_port'] = prompt('[DEFAULT: 22]')
		
		if type(config['annex_remote_port']) is not int:
			if len(config['annex_remote_port']) == 0: config['annex_remote_port'] = 22
		
		if gdrive_auth and 'annex_admin_email' not in config.keys():
			print "We will now attempt to send your public key to the Annex server admin."
			print "You will not be able to add documents to the Annex until it has been"
			print "received by the admin, and properly installed onto the server."
			
			config['annex_admin_email'] = prompt("Admin's email address:")
	
	if 'server_use_ssl' not in config.keys():
		print "Does the Annex server use ssl? (y or n)"
		config['server_use_ssl'] = prompt("[DEFAULT: n] ")
	
	if type(config['server_use_ssl']) is not bool:
		if config['server_use_ssl'] == 'y':
			config['server_use_ssl'] = True
		else:
			config['server_use_ssl'] = False
	
	if 'uv_uuid' not in config.keys():
		config['uv_uuid'] = prompt("What is the Annex server's short name?")
			
	config['web_cookie_secret'] = generateSecureNonce()
	
	with settings(warn_only=True):
		local("mkdir %s" % os.path.join(base_dir, ".monitor"))
		local("mkdir %s" % os.path.join(base_dir, ".users"))
	
	secrets_config = os.path.join(base_dir, "conf", "unveillance.secrets.json")		
	with open(secrets_config, "wb+") as CONFIG:
		CONFIG.write(json.dumps(config))
	
	with open(os.path.join(base_dir, "conf", "local.config.yaml"), 'ab') as LC:
		LC.write("git_annex_dir: %s\n" % git_annex_dir)
		LC.write("encryption.iv: %s\n" % generateSecureRandom())
		LC.write("encryption.salt: %s\n" % generateSecureRandom())
		LC.write("encryption.doc_salt: \"%s\"\n" % generateNonce())
		LC.write("encryption.user_salt: \"%s\"\n" % generateNonce())
	
	sleep(3)
	from Utils.funcs import createNewUser
	createNewUser(admin_username, admin_pwd, as_admin=True)	
	exit(0)