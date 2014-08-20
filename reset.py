from sys import exit
from conf import SERVER_HOST

if __name__ == '__main__':
	if SERVER_HOST not in ["127.0.0.1", "localhost"]: 
		print "NO NEED TO CLEAR ANNEX"
		exit(0)

	print "RESETTING FRONTEND FROM CONFIG...."

	import os, re
	from fabric.api import local, settings

	from conf import ANNEX_DIR, GIT_ANNEX
	
	this_dir = os.getcwd()
	os.chdir(ANNEX_DIR)

	for _, _, files in os.walk(ANNEX_DIR):
		for f in files:
			print "removing %s?" % f
			if re.match(r'\.git/.*', f): continue

			with settings(warn_only=True):
				local("rm %s" % os.path.join(ANNEX_DIR, f))

	with settings(warn_only=True):
		local("%s add ." % GIT_ANNEX)
		local("%s sync" % GIT_ANNEX)
		local("rm -rf %s" % os.path.join(ANNEX_DIR, ".git"))

	os.chdir(this_dir)
	exit(0)