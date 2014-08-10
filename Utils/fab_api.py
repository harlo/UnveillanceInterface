from __future__ import with_statement

import os
from time import time
from fabric.api import *

from conf import DEBUG, SERVER_HOST, getSecrets

def netcat(file, save_as=None, for_local_use_only=False, importer_source="frontend"):
	whoami = "unknown"
	this_dir = os.getcwd()
	op_dir = this_dir

	with settings(warn_only=True):
		whoami = local("whoami", capture=True)
	
	if type(file) is str:
		if save_as is None: save_as = os.path.basename(file)
	else:
		if save_as is None: save_as = "uv_document_%d" % time()

	cmd = [
		"git annex metadata %s --set=importer_source=%s" % (save_as, importer_source),
		"git annex metadata %s --set=imported_by=%s" % (save_as, whoami)
	]
	
	if for_local_use_only: 
		upload_restriction = UPLOAD_RESTRICTION['for_local_use_only']
	else:
		upload_restriction = UPLOAD_RESTRICTION['no_restriction']
	
	cmd.append(".git/hooks/uv-post-netcat \"%s\" %d" % (save_as, upload_restriction))
	
	if SERVER_HOST != "127.0.0.1":
		with settings(warn_only=True):
			res = local("scp -i %s %s:%s/%s" % (
				getSecrets('ssh_key_pub').replace(".pub", ""),
				env.host_string, getSecrets('annex_remote'), save_as), capture=True)

			print res

		cmd = ["ssh -f -i %s %s 'cd %s && %s'" % (getSecrets('ssh_key_pub').replace(".pub", ""), env.host_string, getSecrets('annex_remote'), c) for c in cmd]
	else:
		if type(file) is str:
			cmd.insert(0, "cp %s %s" % (os.path.join(getSecrets('annex_local'), save_as), os.path.join(getSecrets('annex_remote'), save_as)))				
		else:
			with open(os.path.join(getSecrets('annex_remote'), save_as), 'wb+') as F:
				F.write(file)

		op_dir = getSecrets('annex_remote')

	os.chdir(op_dir)

	for c in cmd:
		with settings(warn_only=True):
			res = local(cmd, capture=True)
			if DEBUG: print "RESULT:\n%s" % res

	os.chdir(this_dir)
			
	if DEBUG:
		print "*************\n\n%s\n\n*************" % res
		print "returning"
	
	return res
	