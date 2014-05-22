import threading, os
from subprocess import Popen, PIPE
from fabric.api import execute

from conf import BASE_DIR, DEBUG

class UnveillanceFabricProcess(threading.Thread):
	def __init__(self, func, args=None, op_dir=None):
		self.func = func
		self.args = args
		
		if op_dir is not None:
			self.return_dir = os.getcwd()
			os.chdir(op_dir)
		
		threading.Thread.__init__(self)
		self.start()
	
	def run(self):
		self.output = execute(self.func, **self.args)
		if hasattr(self, "return_dir"): os.chdir(self.return_dir)
		
		