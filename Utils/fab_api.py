import os
from time import time
from fabric.api import *

from conf import DEBUG, getConfig

uv = 'unveillance.local_remote'
env.hosts = [getConfig('%s.hostname', uv)]

def linkLocalRemote():
	if DEBUG: print "linking local remote"
	
	folder = getConfig('%s.folder' % uv)
	remote_path = getConfig('%s.remote_path' % uv)
	uv_user = getConfig('%s.user' % uv)

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

def netcat():
	if DEBUG: print "OH HEY NETCAT"
	
	return False