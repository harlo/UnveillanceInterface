import os, re
from time import sleep

from fabric.api import settings, local

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from conf import DEBUG, ANNEX_DIR, MONITOR_ROOT, getConfig

try:
	from Models.uv_fabric_process import UnveillanceFabricProcess
except ImportError as e:
	if DEBUG: print e
	from lib.Frontend.Models.uv_fabric_process import UnveillanceFabricProcess

try:
	from Utils.fab_api import netcat
except ImportError as e:
	if DEBUG: print e
	from lib.Frontend.Utils.fab_api import netcat

class UnveillanceFSEHandler(FileSystemEventHandler):
	def __init__(self):
		self.watcher_pid_file = os.path.join(MONITOR_ROOT, "watcher.pid.txt")
		self.watcher_log_file = os.path.join(MONITOR_ROOT, "watcher.log.txt")

		self.annex_observer = Observer()
		self.restricted_list = []

		FileSystemEventHandler.__init__(self)

	def set_restricted_in_observer(self, filename):
		if filename not in self.restricted_list:
			self.restricted_list.append(filename)

	def on_created(self, event):
		if event.event_type != "created" : return
		if re.match(re.compile("%s/.*" % os.path.join(ANNEX_DIR, ".git")), event.src_path) is not None: return

		if DEBUG: print "NEW EVENT:\ntype: %s\nis dir: %s\npath: %s\n" % (event.event_type, event.is_directory, event.src_path)

		filename = event.src_path.split("/")[-1]

		this_dir = os.getcwd()
		os.chdir(ANNEX_DIR)
		
		with settings(warn_only=True):
			local("%s add %s" % (getConfig('git_annex_dir'), filename))
			success_tag = False

			netcat_stub = {
				'file' : event.src_path,
				'save_as' : filename
			}

			if filename in self.restricted_list:
				netcat_stub['for_local_use_only'] = True

			p = UnveillanceFabricProcess(netcat, netcat_stub)
			p.join()

			if p.output is not None:
				if DEBUG: print p.output

			if p.error is None:
				success_tag = True
			else:
				if DEBUG: print p.error

			local("%s metadata %s --json --set=uv_uploaded=%s" % (getConfig('git_annex_dir'), filename, str(success_tag)))
	
		os.chdir(this_dir)

	def startAnnexObserver(self):
		self.annex_observer.schedule(self, ANNEX_DIR, recursive=True)
		print "STARTING OBSERVER on %s" % ANNEX_DIR
		self.annex_observer.start()

		startDaemon(self.watcher_log_file, self.watcher_pid_file)
		while True: sleep(1)

	def stopAnnexObserver(self):
		print "STOPPING OBSERVER"
		self.annex_observer.stop()
		self.annex_observer.join()

		stopDaemon(self.watcher_pid_file)
