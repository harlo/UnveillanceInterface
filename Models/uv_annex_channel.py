import os
from time import time
from fabric.api import local, settings

try:
	from lib.Core.Models.uv_task_channel import UnveillanceTaskChannel
except ImportError as e:
	from lib.Frontend.lib.Core.Models.uv_task_channel import UnveillanceTaskChannel

try:
	from lib.Core.Utils.funcs import startDaemon, stopDaemon, generateMD5Hash
except ImportError as e:
	from lib.Frontend.lib.Core.Utils.funcs import startDaemon, stopDaemon, generateMD5Hash

from conf import DEBUG, MONITOR_ROOT
from conf import getSecrets

class UnveillanceAnnexChannel(UnveillanceTaskChannel):
	def __init__(self):

		UnveillanceTaskChannel.__init__(self,
			generateMD5Hash(content=local("whoami", capture=True), salt=time()),
			getSecrets('server_host'), 
			getSecrets('server_message_port'),
			auto_start=False)

	def startAnnexChannel(self):
		startDaemon(self.chan_log_file, self.chan_pid_file)

		with settings(warn_only=True):
			try:
				self.get_socket_info()
			except Exception as e:
				if DEBUG:
					print "ERROR STARTING CONNECTION TO ANNEX MESSENGER:"
					print e

	def stopAnnexChannel(self):
		stopDaemon(self.chan_pid_file)