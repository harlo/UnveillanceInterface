import socket, os

from lib.Frontend.lib.Core.Models.uv_synctask import UnveillanceSyncTask

from conf import DEBUG, ANNEX_DIR, getConfig


class UnveillanceAnnexClient(object):
	def __init__(self):
		if DEBUG: print "ANNEX CLIENT online"
		
		# get the conf settings
		self.hostname = getConfig('unveillance.local_remote.hostname')
		self.port = getConfig('unveillance.local_remote.port')
		self.user = getConfig('unveillance.local_remote.user')
		self.remote_path = getConfig('unveillance.local_remote.remote_path')
		
	def getTasks(self):
		task_ids = []
		for root, dir, files in os.walk(os.path.join(ANNEX_DIR, ".synctasks/local")):
			for file in files:
				if file == "manifest":
					task_ids.append(root.split("/")[-1])
		
		return task_ids
	
	def sendToAnnex(self, data, as_binary=False):
		# tar data 
		# netcat
		# untar
		# tell git-annex to sync
		for required in ['hostname', 'port', 'user', 'remote_path']:
			if not hasattr(self, required): return False
		
		if not as_binary:
			try:
				with open(data, 'rb') as d: data = d.read()
			except IOError as e:
				if DEBUG: print e
				return False
		
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		s.connect((self.hostname, self.port))
		s.sendall(data)
		s.shutdown(socket.SHUT_WR)
		
		while 1:
			res = s.recv(1024)
			if res == "": break
			if DEBUG: print "RES: ", repr(res)
		
		if DEBUG: print "CONNECTION CLOSED."
		s.close()
		
		
		return False
	
	def startTasks(self, _id=None):
		if _id is not None:
			_ids = [_id]
		else:
			_ids = self.getTasks()
			
		for _id in _ids:
			sync_task = UnveillanceSyncTask(_id=_id)
			print sync_task.emit()
	
	def stopTasks(self, _id=None):
		if _id is None:
			_ids = [_id]
		else:
			_ids = self.getTasks()
		
		for _id in _ids:
			sync_task = UnveillanceSyncTask(_id=_id)
			sync_task.stop()