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
	port_prefix = ""

	if port != 22:
		port_prefix += ":%d" % port

	env.hosts = ["%s@%s%s" % (uv_user, hostname, port_prefix)]

def linkLocalRemote():
	if DEBUG: print "linking local remote"
	buildVars()
	
	folder = getConfig('%s.folder' % uv)

	local("git clone ssh://%s@%s%s %s" % (uv_user, env.hosts[0], remote_path, folder))
	local("cd %s" % folder)
	local("mkdir .synctasks")
	local("mkdir .synctasks/local")
	local("echo .DS_Store > .gitignore")
	local("echo *.pyc >> .gitignore")
	local("echo *.exe >> .gitignore")
	local("echo .synctasks/local/ >> .gitignore")
	local("git annex init 'unveillance_remote'")
	local("git annex untrust web")
	local("git remote add unveillance_remote ssh://%s@%s%s" % (
		uv_user, env.hosts[0], remote_path))
	
	return True

def autoSync():
	if DEBUG: print "AUTO SYNC"
	
	buildVars()
	old_dir = os.getcwd()
	result = False

	try:
		from conf import ANNEX_DIR
		with cd(ANNEX_DIR):
			print local("git annex sync")
			result = True
	
	except Exception as e:
		if DEBUG: print e
	
	cd(old_dir)
	return result

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