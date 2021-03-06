from __future__ import with_statement

import os
from time import time
from fabric.api import *

from conf import DEBUG, SERVER_HOST, getConfig, getSecrets
from vars import IMPORTER_SOURCES

def register_upload_attempt(_id):
	res = None
	cmd = "cd %s && .git/hooks/uv-on-upload-attempted \"%s\"" % (
		getSecrets('annex_remote'), _id)

	print "REGISTERING UPLOAD ATTEMPT"

	USE_SSH = getSecrets('server_force_ssh')
	if USE_SSH is None:
		if SERVER_HOST in ["127.0.0.1", "localhost"]:
			USE_SSH = False
		else:
			USE_SSH = True
	
	if USE_SSH:
		env.key_filename = [getSecrets('ssh_key_pub').replace(".pub", "")]

		cmd = "ssh -f -p %d -i %s %s -o IdentitiesOnly=yes 'source ~/.bash_profile && %s'" % (
			getSecrets('annex_remote_port'), env.key_filename[0], env.host_string.split(":")[0], cmd)

	with settings(warn_only=True):
		res = local(cmd, capture=True)

	return res

def netcat(file, save_as=None, alias=None, for_local_use_only=False, importer_source=None):
	whoami = "unknown"
	if importer_source is None or importer_source not in IMPORTER_SOURCES: 
		print "NO IMPORTER SOURCE?"
		return None

	this_dir = os.getcwd()
	op_dir = this_dir

	with settings(warn_only=True):
		whoami = local("whoami", capture=True)
	
	res = []
	if type(file) is str:
		if save_as is None: save_as = os.path.basename(file)
	else:
		if save_as is None: save_as = "uv_document_%d" % time()

	cmd_flags = [
		"--importer_source=%s" % importer_source,
		"--imported_by=%s" % whoami
	]

	if alias is not None:
		cmd_flags.append("--uv_file_alias=\"%s\"" % alias)
	
	if for_local_use_only:
		cmd_flags.append("--uv_local_only=True")
	
	cmd = [
		".git/hooks/uv-post-netcat \"%s\" %s" % (save_as, " ".join(cmd_flags))
	]

	if DEBUG: print "ATTEMPTING NETCAT:\nfile:%s" % save_as

	USE_SSH = getSecrets('server_force_ssh')
	print "USE SSH? %s" % USE_SSH

	if USE_SSH is None:
		if SERVER_HOST in ["127.0.0.1", "localhost"]:
			USE_SSH = False
		else:
			USE_SSH = True
	
	if USE_SSH:
		env.key_filename = [getSecrets('ssh_key_pub').replace(".pub", "")]

		with settings(warn_only=True):
			put_file = os.path.join(getSecrets('annex_remote'), save_as)
			put_cmd = put(file, put_file)
			
			if DEBUG: print put_cmd

			if len(put_cmd) == 0 or put_cmd[0] != put_file:
				return None

			res.append(put_cmd)

		use_hostname = env.host_string.split(":")[0]

		cmd = ["ssh -f -p %d -i %s %s -o IdentitiesOnly=yes 'cd %s && source ~/.bash_profile && %s'" % (
			getSecrets('annex_remote_port'), env.key_filename[0], use_hostname, getSecrets('annex_remote'), c) for c in cmd]
	else:
		if type(file) in [str, unicode]:
			with settings(warn_only=True):
				res.append(local("mv %s %s" % (os.path.join(getSecrets('annex_local'), save_as), os.path.join(getSecrets('annex_remote'), save_as)), capture=True))			
		else:
			with open(os.path.join(getSecrets('annex_remote'), save_as), 'wb+') as F:
				F.write(file.getvalue())
				file.close()

		op_dir = getSecrets('annex_remote')

	os.chdir(op_dir)

	if DEBUG: 
		print "\n\nNOW LAUNCHING NETCAT COMMANDS (%d)" % len(cmd)	
		print "in dir %s" % os.getcwd()

	for c in cmd:
		if DEBUG: print "\n%s\n" % c
		res.append(local(c, capture=True))

	os.chdir(this_dir)
			
	if DEBUG:
		print "*************\n\n%s\n\n*************" % res
		print "returning from netcat."
	
	return res
	