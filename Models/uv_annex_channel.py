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
	def __init__(self):

		self.chan_pid_file = os.path.join(MONITOR_ROOT, "chan.pid.txt")
		self.chan_log_file = os.path.join(MONITOR_ROOT, "chan.log.txt")

		use_ssl = None
		try:
			use_ssl = getSecrets('server_message_use_ssl')
		except Exception as e:
			print e

		UnveillanceTaskChannel.__init__(self,
			"annex_channel", getSecrets('server_host'), getSecrets('server_message_port'),
			use_ssl=use_ssl, auto_start=False)

	def route_annex_channel_message(self, message):
		super(UnveillanceAnnexChannel, self).route_annex_channel_message(message)

		if DEBUG:
			print "ALSO HERE IS MESSAGE IN FRONTEND!"

	def startAnnexChannel(self):
		startDaemon(self.chan_log_file, self.chan_pid_file)
		self.get_socket_info()
		
	def stopAnnexChannel(self):
		self.die()
		stopDaemon(self.chan_pid_file)