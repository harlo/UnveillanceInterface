import os
from sys import argv, exit

if __name__ == "__main__":
	base_dir = os.getcwd()
	
	if len(argv) == 1:
		return_dir = base_dir
		launch_frontend = True
		ssh_root = "~/.ssh"
		server_host = "127.0.0.1"
		server_port = 8888
		server_use_ssl = False
	elif len(argv) == 6:
		return_dir = argv[1]
		launch_frontend = False
		ssh_root = argv[2]
		server_host = argv[3]
		server_port = argv[4]
		server_use_ssl = argv[5]
	else:
		print "NO, these are not the right set of args."
		exit(1)
	
	local_config = os.path.join(base_dir, "conf", "local.config.yaml")
	secrets_config = os.path.join(return_dir, "conf", "unveillance.secrets.json")
	
	from fabric.api import local
	from fabric.operations import prompt
	from json import loads, dumps
	
	local("mkdir %s" % os.path.join(base_dir, ".monitor"))
	local("mkdir %s" % os.path.join(base_dir, "tmp"))
	
	print "Unveillance will now generate a public/private key pair for communication with the server..."
	
	from time import time
	lm_key_pwd = prompt("Please enter a good password for this key:")
	lm_key = os.path.join(ssh_root, "unveillance.%d.key" % time())
	local("ssh-keygen -f %s -t rsa -b 4096 -N %s" % (lm_key, lm_key_pwd))
	
	with open(local_config, "ab") as CONFIG:
		CONFIG.write("ssh_root: %s\n" % ssh_root)
		CONFIG.write("server.host: %s\n" % server_host)
		CONFIG.write("server.port: %s\n" % server_port)
		CONFIG.write("server.use_ssl: %s\n" % server_use_ssl)
		
		from lib.Core.Utils.funcs import generateSecureNonce
		CONFIG.write("api.web.cookie_secret: %s\n" % generateSecureNonce())
		
		try:
			with open(secrets_config, "rb") as LM_S:
				secrets = loads(LM_S.read())
				lm_secrets = secrets['unveillance.local_remote']
		except Exception as e: 
			lm_secrets = {}
			secrets = {}
			
		if len(lm_secrets.keys()) == 0:
			print "No setup variables available.  Please set the following:"
		
		try:
			lm_local_path = lm_secrets['local_path']
		except Exception as e:
			lm_local_path = prompt("Where do you want your Unveillance folder?  The folder should not exist, and type the full path please:")
			lm_secrets['local_path'] = lm_local_path
		
		try:
			lm_user = lm_secrets['user']
		except Exception as e:
			lm_user = prompt("What's the remote's username?")
			lm_secrets['user'] = lm_user
			
		try:
			lm_hostname = lm_secrets['hostname']
		except Exception as e:
			lm_hostname = prompt("What is the remote's hostname?")
			lm_secrets['hostname'] = lm_hostname
		
		try:
			lm_port = lm_secrets['port']
		except Exception as e:
			lm_port = prompt("What port will the app use to connect to the remote via SSH?")
			lm_secrets['port'] = lm_port
		
		try:
			lm_remote_path = lm_secrets['remote_path']
		except Exception as e:
			lm_remote_path = prompt("What is the full path to the remote's Unveillance folder?")
			lm_secrets['remote_path'] = lm_remote_path
		
		try:
			lm_uuid = lm_secrets['uv_uuid']
		except Exception as e:
			lm_uuid = prompt("What is the UUID for the remote?  (If you don't know, leave blank)")
			if len(lm_uuid) == 0:
				lm_uuid = generateSecureNonce()
			
			lm_secrets['uv_uuid'] = lm_uuid
		
		lm_secrets['pwd'] = lm_key_pwd
		
		secrets['unveillance.local_remote'].update(lm_secrets)
		with open(secrets_config, "wb+") as LM_S: LM_S.write(dumps(secrets))
		# TODO: AES encrypt secrets file, secure-delete the cruft
		
		CONFIG.write("unveillance.local_remote.local_path: %s\n" % lm_local_path)
		CONFIG.write("unveillance.local_remote.port: %s\n" % lm_port)
		CONFIG.write("unveillance.local_remote.hostname: %s\n" % lm_hostname)
		CONFIG.write("unveillance.local_remote.user: %s\n" % lm_user)
		CONFIG.write("unveillance.local_remote.remote_path: %s\n" % lm_remote_path)
		CONFIG.write("unveillance.local_remote.pub_key: %s.pub\n" % lm_key)
		CONFIG.write("unveillance.uv_uuid: %s\n" % lm_uuid)
	
	os.chdir(os.path.join(base_dir, "lib", "Core"))
	local("pip install --upgrade -r requirements.txt")
	
	os.chdir(base_dir)
	local("pip install --upgrade -r requirements.txt")
	
	if launch_frontend:
		local("python unveillance_frontend.py -firstuse")
	else:
		os.chdir(return_dir)

	exit(0)