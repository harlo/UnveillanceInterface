from lib.Core.Models.uv_synctask import UnveillanceSyncTask as UVST_Stub
from lib.Core.vars import EmitSentinel
from uv_object import UnveillanceObject

class UnveillanceSyncTask(UnveillanceObject, UVST_Stub):
	def __init__(self, **args):
		UVST_Stub.__init__(self)
		UnveillanceObject.__init__(self, _id=_id, inflate=inflate, 
			emit_sentinels=[EmitSentinel("cronjob", "CronTab", None)])
	
	def start(self):
		if not super(UnveillanceSyncTask, self).start():
			super(UnveillanceSyncTask, self).invalidate(error="Could not start SyncTask")
		self.save()
		
	def stop(self):
		if not super(UnveillanceSyncTask, self).stop():
			super(UnveillanceSyncTask, self).invalidate(error="Could not stop SyncTask")
		self.save()
	
	def save(self):
		if hasattr(self, 'cron_job') and self.cron_job is not None:
			self.is_running = self.cron_job.is_enabled()
		
		UVST_Stub.save(self)
		UnveillanceObject.save(self)