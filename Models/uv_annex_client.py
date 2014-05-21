from multiprocessing import Process
from fabric.tasks import execute

from lib.Frontend.Utils.fab_api import netcat, autoSync

from conf import DEBUG, getConfig

class UnveillanceAnnexClient(object):
	def __init__(self):
		if DEBUG: print "ANNEX CLIENT online"
		
		# get the conf settings
		try:
			self.hostname = getConfig('unveillance.local_remote.hostname')
		except KeyError as e: pass
		
		try:
			self.port = getConfig('unveillance.local_remote.port')
		except KeyError as e: pass
		
		try:
			self.user = getConfig('unveillance.local_remote.user')
		except KeyError as e: pass
		
		try:
			self.remote_path = getConfig('unveillance.local_remote.remote_path')
		except KeyError as e: pass
		
	def getTasks(self):
		try:
			from conf import ANNEX_DIR
		except ImportError as e:
			if DEBUG: print e
			return None

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
		
		return None
	
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