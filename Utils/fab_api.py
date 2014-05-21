from __future__ import with_statement

import os
from time import time
from fabric.api import *

from conf import DEBUG, getConfig

uv = 'unveillance.local_remote'

def buildVars():
	uv_user = getConfig('%s.user' % uv)
	remote_path = getConfig('%s.remote_path' % uv)
	hostname = getConfig('%s.hostname' % uv)
	port = getConfig('%s.port' % uv)
	folder = getConfig('%s.folder' % uv)
	port_prefix = ""

	if port != 22:
		port_prefix += ":%d" % port

	env.hosts = ["%s@%s%s" % (uv_user, hostname, port_prefix)]
	
	return {
		'uv_user' : uv_user,
		'remote_path' : remote_path,
		'hostname' : hostname,
		'port' : port,
		'folder' : folder
	}

def linkLocalRemote():
	if DEBUG: print "linking local remote"
	vars = buildVars()
	
	old_dir = os.getcwd()
	local("git clone ssh://%s%s %s" % (env.hosts[0], vars['remote_path'], vars['folder']))

	os.chdir(vars['folder'])
	local("pwd")
	local("mkdir .synctasks")
	local("mkdir .synctasks/local")
	local("echo .DS_Store > .gitignore")
	local("echo *.pyc >> .gitignore")
	local("echo *.exe >> .gitignore")
	local("echo .synctasks/local/ >> .gitignore")
	local("git annex init 'unveillance_remote'")
	local("git remote add unveillance_remote ssh://%s%s" % (
		env.hosts[0], vars['remote_path']))
	local("git annex status")

	os.chdir(old_dir)
	return True

def autoSync():
	if DEBUG: print "AUTO SYNC"
	
	'''
	buildVars()
	old_dir = os.getcwd()
	result = False

	from conf import ANNEX_DIR
	if not os.path.exists(ANNEX_DIR): return False
	
	os.chdir(ANNEX_DIR)
	sync_result = local("git annex sync", capture=True)
	if DEBUG: 
		print "TASK STUFF"
		print sync_result.failed
	
	if not sync_result.failed: result = True	
	
	
	os.chdir(old_dir)
	print "AUTO SYNC RESULT: %s" % result
	return result
	'''
	return True

def netcat(file=None):
	if DEBUG: print "OH HEY NETCAT"
	if file is None: return False
	
	old_dir = os.getcwd()
	result = False
	
	from conf import ANNEX_DIR
	try:
		with cd(ANNEX_DIR):
			put(file, os.path.join(remote_path, file))
			run("cd %s" % remote_path)
			run("git annex sync")
			result = True
	
	except Exception as e:
		if DEBUG: print e
	
	cd(old_dir)
	return result