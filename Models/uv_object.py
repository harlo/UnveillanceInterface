from lib.Core.Models.uv_object import UnveillanceObject as UVO_Stub

class UnveillanceObject(UVO_Stub):
	def __init__(self, **args):
		super(UnveillanceObject, self).__init__(**args)

	def save(self):
		print "SAVING FROM FRONTEND"
		# TODO: HOW??