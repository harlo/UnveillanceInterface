from __future__ import with_statement

import os
from time import time
from fabric.api import *

from conf import DEBUG, getConfig

uv = 'unveillance.local_remote'

def test(h):
	if DEBUG: print "TESTING FAB with arg: %s" % h
			
	x = local("pwd")
	print "RES: %s" % x
	
	return True

def netcat(file, password, save_as=None, remote_path=None):
	if DEBUG: print "NETCATTING FILE"
	
	env.key_filename = [getConfig("%s.pub_key" % uv)]
	env.password = password
	
	if remote_path is None:
		remote_path = getConfig("%s.remote_path" % uv)
	
	if type(file) is str:
		if save_as is None: save_as = os.path.basename(file)
	else:
		if save_as is None: save_as = "uv_document_%d" % time()
	
	print save_as
	res = put(file, os.path.join(remote_path, save_as))
	with cd(remote_path):
		cmd = ".git/hooks/post-receive \"%s\"" % save_as
		res = run(cmd)

		print "*************\n\n%s\n\n*************" % res
	
		print "returning"

	return res

def linkLocalRemote():
	if DEBUG: print "linking local remote"
	
	remote_path = getConfig("%s.remote_path" % uv)
	local_folder = getConfig("%s.folder" % uv)
	
	local("git clone ssh://%s%s %s" % (hosts[0], remote_path, local_folder))

	os.chdir(local_folder)
	local("mkdir .synctasks")
	local("mkdir .synctasks/local")
	local("echo .DS_Store > .gitignore")
	local("echo *.pyc >> .gitignore")
	local("echo *.exe >> .gitignore")
	local("echo .synctasks/local/ >> .gitignore")
	local("git annex init 'unveillance_remote'")
	local("git remote add unveillance_remote ssh://%s%s" % (hosts[0],
		remote_path, local_folder))
	local("git annex status")
	
	return True

def initLocalRemote():
	if DEBUG: print "initing local remote"
	
	# TODO: this can be fabric rather than bash...	

def autoSync():
	if DEBUG: print "AUTO SYNC"
	
	return local("git annex sync")
	