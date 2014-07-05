from __future__ import with_statement

import os
from time import time
from fabric.api import *

from conf import DEBUG, SERVER_HOST, getSecrets

def netcat(file, save_as=None, remote_path=None):
	if DEBUG: print "NETCATTING FILE"
	
	if type(file) is str:
		if save_as is None: save_as = os.path.basename(file)
	else:
		if save_as is None: save_as = "uv_document_%d" % time()
		
	cmd = ".git/hooks/uv-post-netcat \"%s\"" % save_as
	print cmd
	
	if SERVER_HOST != "127.0.0.1":
	
		env.key_filename = [getSecrets('ssh_key_pub').replace(".pub", '')]
		env.password = getSecrets('ssh_key_pwd')
		# TODO: port if not 22?
	
		annex_base = getSecrets('annex_remote')
	
		if remote_path is None:
			remote_path = annex_base
		else:
			remote_path = os.path.join(annex_base, remote_path)
		
		with settings(warn_only=True):
			res = put(file, os.path.join(remote_path, save_as))
			if DEBUG: 
				print "FOR BETTER OR WORSE:\n%s" % res
		
		with settings(warn_only=True):
			with cd(annex_base):
				res = run(cmd)
				if DEBUG:
					print "AFTER SECOND RUN:\n%s" % res
	else:				
		this_dir = os.getcwd()
		with settings(warn_only=True):
			os.chdir(getSecrets('annex_local'))
			res = local(cmd)
			os.chdir(this_dir)
			
	if DEBUG:
		print "*************\n\n%s\n\n*************" % res
		print "returning"
	
	return res
	