from uv_object import UnveillanceObject

class CompassAnnex(UnveillanceObject):
	def __init__(self, inflate=None, _id=None):
		super(CompassAnnex, self).__init__(inflate=inflate, _id=_id)
	
	def create(self):
		# 1. query server to get ports
		# 2. update config with port

		# 3. modify ssh config (host, identity file, port)
		# 4. make first contact to establish trust
		# 5. init git-annex on dir
		# 6. link local to remote

	def save(self):
		print self.emit()