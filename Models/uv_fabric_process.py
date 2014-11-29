import threading, os
from fabric.api import execute

from conf import BASE_DIR, DEBUG, SERVER_HOST, getSecrets

class UnveillanceFabricProcess(threading.Thread):
	def __init__(self, func, args=None, op_dir=None):
		self.func = func
		
		if args is not None: self.args = args
		else: self.args = {}
		
		self.output = None
		self.error = None
		
		USE_SSH = getSecrets('server_force_ssh')
		if USE_SSH is None:
			if SERVER_HOST in ["127.0.0.1", "localhost"]:
				USE_SSH = False
			else:
				USE_SSH = True
		
		if USE_SSH:
			uv_user = getSecrets("server_user")
			hostname = getSecrets("server_host")
			port = getSecrets("annex_remote_port")
			
			port_prefix = ""
			if port is not None and port != 22:
				port_prefix += ":%d" % port
				
			self.args.update({
				'hosts' : ["%s@%s%s" % (uv_user, hostname, port_prefix)]
			})
				
		if op_dir is not None:
			self.return_dir = os.getcwd()
			os.chdir(op_dir)
		
		threading.Thread.__init__(self)
		self.start()
	
	def run(self):
		try:
			res = execute(self.func, **self.args)
			self.output = res[res.keys()[0]]
		except Exception as e:
			if DEBUG: print "THERE WAS AN ERROR EXECUTING THIS THREAD"
			self.error = e
			
		if hasattr(self, "return_dir"): os.chdir(self.return_dir)
		
		