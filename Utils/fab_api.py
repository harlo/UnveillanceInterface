from __future__ import with_statement

import os
from time import time
from fabric.api import *

from conf import DEBUG, SERVER_HOST, getConfig, getSecrets
from vars import IMPORTER_SOURCES

def netcat(file, save_as=None, alias=None, for_local_use_only=False, importer_source=None):
	whoami = "unknown"
	if importer_source is None or importer_source not in IMPORTER_SOURCES: return None

	this_dir = os.getcwd()
	op_dir = this_dir

	with settings(warn_only=True):
		whoami = local("whoami", capture=True)
	
	res = []
	if type(file) is str:
		if save_as is None: save_as = os.path.basename(file)
	else:
		if save_as is None: save_as = "uv_document_%d" % time()

	cmd = [
		"git-annex add \"%s\"" % save_as,
		"git-annex metadata \"%s\" --set=importer_source=%s" % (save_as, importer_source),
		"git-annex metadata \"%s\" --set=imported_by=%s" % (save_as, whoami)
	]

	if alias is not None:
		cmd.append("git-annex metadata \"%s\" --set=uv_file_alias=\"%s\"" % (save_as, alias))
	
	if for_local_use_only:
		cmd.append("git-annex metadata \"%s\" --set=uv_local_only=True" % save_as)
	
	cmd.extend([
		"git-annex sync",
		".git/hooks/uv-post-netcat \"%s\"" % save_as
	])

	if DEBUG: print "ATTEMPTING NETCAT:\nfile:%s" % save_as
	
	if SERVER_HOST not in ["127.0.0.1", "localhost"]:
		env.key_filename = [getSecrets('ssh_key_pub').replace(".pub", "")]

		with settings(warn_only=True):
			put_file = os.path.join(getSecrets('annex_remote'), save_as)
			put_cmd = put(file, put_file)
			
			if DEBUG: print put_cmd

			if len(put_cmd) == 0 or put_cmd[0] != put_file:
				return None

			res.append(put_cmd)

		cmd = ["ssh -f -i %s %s 'cd %s && source ~/.bash_profile && %s'" % (getSecrets('ssh_key_pub').replace(".pub", ""), env.host_string, getSecrets('annex_remote'), c) for c in cmd]
	else:
		if type(file) in [str, unicode]:
			with settings(warn_only=True):
				res.append(local("mv %s %s" % (os.path.join(getSecrets('annex_local'), save_as), os.path.join(getSecrets('annex_remote'), save_as)), capture=True))			
		else:
			with open(os.path.join(getSecrets('annex_remote'), save_as), 'wb+') as F:
				F.write(file.getvalue())
				file.close()

		for i, c in enumerate(cmd):
			if i != len(cmd) - 1:
				cmd[i] = "%s/%s" % (getConfig('git_annex_dir'), c)

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
	