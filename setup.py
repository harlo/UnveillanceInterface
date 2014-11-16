import os, re, json
from time import time, sleep
from sys import argv, exit
from fabric.api import local, settings
from fabric.operations import prompt
from fabric.context_managers import hide

from lib.Core.Utils.funcs import generateSecureNonce, generateSecureRandom, generateNonce
from conf import DEBUG

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
	print argv[1]
	
	if len(argv[1]) > 3:		
		try:
			with open(argv[1], 'rb') as CONF:
				config.update(json.loads(CONF.read()))
		except Exception as e:
			print "No pre-set configurations.  That's fine: we'll get you started!"
			if DEBUG: print e
		
	print "\n****************************"
	print "Hello.  Welcome to Unveillance Frontend setup."
	admin_username = prompt("Choose a username:")
	admin_pwd = prompt("Pick a good password:")

	print "****************************\n"

	with settings(warn_only=True):
		SYS_ARCH = local("uname -m", capture=True)
	
	if 'api.port' not in config.keys():
		print "\n****************************"
		print "What port should the frontend run on?"
		config['api.port'] = prompt("[DEFAULT: 8888]")
	
	if type(config['api.port']) is not int:
		if len(config['api.port']) == 0: 
			config['api.port'] = 8888
		else:
			try:
				config['api.port'] = int(config['api.port'])
			except ValueError as e:
				print "WARN: could not be sure %s is a number.  Using 8888 instead." % config['api.port']
				config['api.port'] = 8888
	
	gdrive_auth = False
	if 'auth_storage' in config.keys():
		gdrive_auth = True
	else:
		if 'gdrive_auth_no_ask' not in config.keys() or not config['gdrive_auth_no_ask']:
			print "\n****************************"
			print "Google Drive Authentication:"
			print "If you want to to use Google Drive to import documents into the Annex server, you must authenticate the application by visiting the URL below."
			print "You will be shown an authentication code that you must paste into this terminal when prompted."
			print "Authenticate Google Drive? y or n"
			
			if prompt("[DEFAULT: n]") == "y": gdrive_auth = True
			else: print "****************************\n"
	
	if gdrive_auth:
		config.update({
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
		
		if 'auth_storage' not in config.keys():
			from oauth2client.client import OAuth2WebServerFlow
			from oauth2client.file import Storage
		
			config['auth_storage'] = os.path.join(base_dir, "conf", "drive.secrets.json")
			flow = OAuth2WebServerFlow(config['client_id'], config['client_secret'],
				config['scopes'], config['redirect_url'])
		
			print "To use Google Drive to import documents into the Annex server, you must authenticate the application by visiting the URL below."
			print "You will be shown an authentication code that you must paste into this terminal when prompted."
			print "URL:\n\n%s\n" % flow.step1_get_authorize_url()
			credentials = flow.step2_exchange(prompt("Code: "))
			Storage(config['auth_storage']).put(credentials)

		print "****************************\n"
	
	if 'server_host' not in config.keys():
		print "\n****************************"
		print "What is the Public IP/hostname of the Annex server?"
		config['server_host'] = prompt("[DEFAULT: localhost] ")
		
		if len(config['server_host']) == 0:
			config['server_host'] = "127.0.0.1"
		
		print "****************************\n"

	if 'server_force_ssh' not in config.keys():
		if config['server_host'] in ["127.0.0.1", "localhost"]:
			print "\n****************************"
			print "Although the Annex server is on local host, this could be a proxy."
			print "Treat Annex server as a proxy? [y or n]"
			config['server_force_ssh'] = prompt("[DEFAULT: n] ")

			if config['server_force_ssh'] == "y":
				config['server_force_ssh'] = True
			else:
				config['server_force_ssh'] = False

	if config['server_host'] not in ["127.0.0.1", "localhost"]:
		config['server_force_ssh'] = True

	if 'annex_local' not in config.keys():
		print "\n****************************"
		print "Where do you want your Unveillance folder?  The folder should not exist."
		config['annex_local'] = prompt("[DEFAULT: ~/unveillance_local]")
		print "****************************\n"

	if len(config['annex_local']) == 0:
		config['annex_local'] = os.path.join(os.path.expanduser("~"), "unveillance_local")
	
	git_annex_dir = locateLibrary(r'git-annex\.*')
	if git_annex_dir is None:
		with settings(warn_only=True):
			if SYS_ARCH == "i686":
				arch = "git-annex-standalone-i386.tar.gz"
			else:
				arch = "git-annex-standalone-amd64.tar.gz"

			local("wget -O lib/git-annex.tar.gz http://downloads.kitenet.net/git-annex/linux/current/%s" % arch)
			local("tar -xvzf lib/git-annex.tar.gz -C lib")
			local("rm lib/git-annex.tar.gz")
	
		git_annex_dir = locateLibrary(r'git-annex\.*')

	# init local repo
	with settings(warn_only=True):
		local("mkdir %s" % config['annex_local'])

	if git_annex_dir is not None:
		GIT_ANNEX = os.path.join(git_annex_dir, "git-annex")
		
		this_dir = os.getcwd()
		os.chdir(config['annex_local'])

		with settings(warn_only=True):
			local("git init")
			local("git config annex.genmetadata true")
			local("%s init unveillance_local" % GIT_ANNEX)
			local("%s untrust web" % GIT_ANNEX)
			local("%s direct" % GIT_ANNEX)

		os.chdir(this_dir)

	if 'server_port' not in config.keys():
		print "\n****************************"
		print "What port is the Annex server on?"
		config['server_port'] = prompt("[DEFAULT: 8889] ")
		print "****************************\n"
	
	if type(config['server_port']) is not int:
		if len(config['server_port']) == 0: 
			config['server_port'] = 8889
		else:
			try:
				config['server_port'] = int(config['server_port'])
			except ValueError as e:
				print "WARN: could not be sure %s is a number.  Using 8889 instead." % config['server_port']
				config['server_port'] = 8889

	if 'server_message_port' not in config.keys():
		print "\n****************************"
		print "What port does the Annex server send messages over?"
		config['server_message_port'] = prompt("[DEFAULT: %d] " % (config['server_port'] + 1))

		if len(config['server_message_port']) == 0:
			config['server_message_port'] = (config['server_port'] + 1)
		else:
			try:
				config['server_message_port'] = int(config['server_message_port'])
			except ValueError as e:
				print "WARN: could not be sure %s is a number.  Using %d instead." % (
					config['server_message_port'], (config['server_port'] + 1))
				
				config['server_message_port'] = (config['server_port'] + 1)

		print "****************************\n"
	
	if 'annex_remote' not in config.keys():
		print "\n****************************"
		print "What is the path to the Annex's repository?"
		config['annex_remote']  = prompt("[DEFAULT: ~/unveillance_remote]")
		print "****************************\n"
	
	if len(config['annex_remote']) == 0:
		if not config['server_force_ssh']:
			config['annex_remote'] = os.path.join(os.path.expanduser("~"),
				"unveillance_remote")
		else:
			config['annex_remote'] = "~/unveillance_remote"
	
	if not config['server_force_ssh']: 
		config['server_use_ssl'] = False
	else:
		if 'ssh_root' not in config.keys():
			print "\n****************************"
			print "Where is your ssh folder?"
			config['ssh_root'] = prompt("[DEFAULT: ~/.ssh] ")
			print "****************************\n"
		
		if len(config['ssh_root']) == 0:
			config['ssh_root'] = os.path.join(os.path.expanduser("~"), ".ssh")

		if 'ssh_key_priv' not in config.keys():
			print "Unveillance will now generate a public/private key pair for communication with the server"
			config['ssh_key_pwd'] = generateNonce(top_range=59, bottom_range=29)
			config['ssh_key_priv'] = os.path.join(config['ssh_root'],
				"unveillance.%d.key" % time())
			config['ssh_key_pub'] = "%s.pub" % config['ssh_key_priv']
		
			with settings(warn_only=True):
				'''
				local("ssh-keygen -f %s -t rsa -b 4096 -N %s" % (config['ssh_key_priv'],
					config['ssh_key_pwd']))
				'''
				local('ssh-keygen -f %s -t rsa -b 4096 -N ""' % config['ssh_key_priv'])
				print "****************************\n"

		if git_annex_dir is not None:			
			this_dir = os.getcwd()
			os.chdir(config['annex_local'])

			key_name = [s for s in config['ssh_key_pub'].split('/') if s != ''][-1]

			with settings(warn_only=True):
				local("cp %s %s" % (config['ssh_key_pub'], config['annex_local']))
				local("%s metadata %s --json --set=uv_never_upload=True" % (GIT_ANNEX, key_name))
				local("%s add %s" % (GIT_ANNEX, key_name))

			os.chdir(this_dir)
		else:
			with settings(warn_only=True):
				# copy public key into annex local only
				local("cp %s %s" % (config['ssh_key_pub'], config['annex_local']))
		
		if 'server_user' not in config.keys():
			print "\n****************************"
			config['server_user'] = prompt("What user name should SSH use? : ")
			print "****************************\n"
		
		if 'annex_remote_port' not in config.keys():
			print "\n****************************"
			print "What port does the Annex server SSH to?"
			config['annex_remote_port'] = prompt('[DEFAULT: 22]')
			print "****************************\n"
		
		if type(config['annex_remote_port']) is not int:
			if len(config['annex_remote_port']) == 0:
				config['annex_remote_port'] = 22
		
		print "*************** ATTENTION ******************"
		
		if gdrive_auth and 'annex_admin_email' not in config.keys():
			print "When you first log in, we will attempt to send your public key to the Annex server admin."
			print "You will not be able to add documents to the Annex until it has been"
			print "received by the admin, and properly installed onto the server."
			
			config['annex_admin_email'] = prompt("Admin's email address:")
		else:
			print "Your public key needs to be sent to the Annex's administrator before you can upload anything."
			print "Your public key is in your local Unveillance folder (%s)." % config['annex_local']
			print "How you send this key is up to you!"
		
		print "*********************************"
	
	if 'server_use_ssl' not in config.keys():
		print "\n****************************"
		print "Does the Annex server use ssl? (y or n)"
		config['server_use_ssl'] = prompt("[DEFAULT: n] ")
		print "****************************\n"
	
	if type(config['server_use_ssl']) is not bool:
		if config['server_use_ssl'] == 'y':
			config['server_use_ssl'] = True
		else:
			config['server_use_ssl'] = False
	
	if 'uv_uuid' not in config.keys():
		print "\n****************************"
		config['uv_uuid'] = prompt("What is the Annex server's short name?")
		print "****************************\n"
			
	config['web_cookie_secret'] = generateSecureNonce()
	
	with settings(hide('everything'), warn_only=True):
		local("rm -rf %s" % os.path.join(base_dir, ".users"))
	
	with settings(hide('everything'), warn_only=True):
		local("rm -rf %s" % os.path.join(base_dir, ".monitor"))

	with settings(hide('everything'), warn_only=True):		
		local("mkdir %s" % os.path.join(base_dir, ".monitor"))
	
	with settings(hide('everything'), warn_only=True):
		local("mkdir %s" % os.path.join(base_dir, ".users"))
	
	secrets_config = os.path.join(base_dir, "conf", "unveillance.secrets.json")		
	with open(secrets_config, "wb+") as CONFIG:
		CONFIG.write(json.dumps(config))
	
	with open(os.path.join(base_dir, "conf", "local.config.yaml"), 'ab') as LC:
		try:
			LC.write("git_annex_dir: %s\n" % git_annex_dir)
		except NameError as e: pass

		LC.write("encryption.iv: %s\n" % generateSecureRandom())
		LC.write("encryption.salt: %s\n" % generateSecureRandom())
		LC.write("encryption.doc_salt: \"%s\"\n" % generateNonce())
		LC.write("encryption.user_salt: \"%s\"\n" % generateNonce())
		LC.write("api.port: %d\n" % config['api.port'])
		LC.write("sys_arch: %s\n" % SYS_ARCH)

		with settings(hide('everything'), warn_only=True):
			LC.write("python_home: %s\n" % local("which python", capture=True))
	
	sleep(3)
	from Utils.funcs import createNewUser
	createNewUser(admin_username, admin_pwd, as_admin=True)	
	exit(0)