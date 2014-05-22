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

def test(h):
	if DEBUG: print "TESTING FAB with arg: %s" % h
	
	vars = buildVars()
	if DEBUG: print vars
		
	x = local("pwd", capture=True)
	print "RES: %s" % x
	
	return True

def linkLocalRemote():
	if DEBUG: print "linking local remote"
	
	vars = buildVars()
	local("git clone ssh://%s%s %s" % (env.hosts[0], vars['remote_path'], vars['folder']))

	os.chdir(vars['folder'])
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
	
	return True

def autoSync():
	if DEBUG: print "AUTO SYNC"
	
	return local("git annex sync")
	