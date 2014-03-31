from lib.Core.Models.uv_synctask import UnveillanceSyncTask as UVST_Stub
from uv_object import UnveillanceObject

class UnveillanceSyncTask(UnveillanceObject, UVST_Stub):
	def __init__(self, **args):
		UVST_Stub.__init__(self)
		
		emit_sentinels=EmitSentinel("cronjob", "CronTab", None)
		
		UnveillanceObject.__init__(self, _id=_id, inflate=inflate,
			emit_sentinels=emit_sentinels)
	
	def save(self):
		UVST_Stub.save(self)
		UnveillanceObject.save(self)