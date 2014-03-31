from crontab import CrontTab
from uv_object import UnveillanceObject

class UnveillanceSyncTask(UnveillanceObject):
	def __init__(self, **args):
		emit_sentinels=EmitSentinel("cronjob", "CronTab", None)
	
		if inflate is not None:
			inflate['is_running'] = False
		
		super(UnveillanceSyncTask, self).__init__(_id=_id, inflate=inflate,
			emit_sentinels=emit_entinels)
	
	def setupCronJob(self):
		# TODO: THIS IS NOT PLATFORM-AGNOSTIC
		cron = CronTab(user=True)
		cron_job = cron.new(command=self.command, comment=self._id)
		
		if self.frequency == "m": cron_job.minute.every(self.duration)
		elif self.frequency == "h": cron_job.hour.every(self.duration)
		elif self.frequency == "d": cron_job.day.every(self.duration)
		
		return cron_job
	
	def start(self):
		if hasattr(self, 'cron_job') and self.cron_job is not None:
			if not self.cron_job.is_valid(): return False
			if self.cron_job.is_enabled(): return False
			
			self.cron_job.enable()			
			self.save()
			
			return self.cron_job.is_enabled()
		
		return False
		
	def stop(self):
		if hasattr(self, 'cron_job') and self.cron_job is not None:
			if not self.cron_job.is_valid(): return False
			if not self.cron_job.is_enabled(): return False
			
			self.cron_job.enable(False)
			self.save()
			
			return not self.cron_job.is_enabled()
			
		return False
	
	def locateCronJob(self, init=False):
		try:
			return cron.find_comment(self._id)][0]
		except Exception as e: 
			print e
			if init: return setupCronJob()
			
		return None
	
	def inflate(self, inflate):
		super(UnveillanceSyncTask, self).inflate(inflate)
		
		self.cron_job = self.locateCronJob(init=True)
	
	def save(self):
		if hasattr(self, 'cron_job') and self.cron_job is not None:
			self.is_running = self.cron_job.is_enabled()
	
		super(UnveillanceSyncTask, self).save()