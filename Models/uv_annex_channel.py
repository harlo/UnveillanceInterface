import os
from time import time

try:
	from lib.Core.Models.uv_task_channel import UnveillanceTaskChannel
except ImportError as e:
	from lib.Frontend.lib.Core.Models.uv_task_channel import UnveillanceTaskChannel

try:
	from lib.Core.Utils.funcs import startDaemon, stopDaemon
except ImportError as e:
	from lib.Frontend.lib.Core.Utils.funcs import startDaemon, stopDaemon

from conf import DEBUG, MONITOR_ROOT
from conf import getSecrets

class UnveillanceAnnexChannel(UnveillanceTaskChannel):
	def __init__(self, chan_id):

		self.chan_pid_file = os.path.join(MONITOR_ROOT, "chan.pid.txt")
		self.chan_log_file = os.path.join(MONITOR_ROOT, "chan.log.txt")

		self.chan_id = chan_id

	def startAnnexChannel(self):
		startDaemon(self.chan_log_file, self.chan_pid_file)

		UnveillanceTaskChannel.__init__(self,
			self.chan_id, getSecrets('server_host'), getSecrets('server_message_port'))

	def stopAnnexChannel(self):
		self.die()
		stopDaemon(self.chan_pid_file)