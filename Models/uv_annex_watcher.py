import os, re
from time import sleep

from fabric.api import settings, local

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from conf import DEBUG, ANNEX_DIR, MONITOR_ROOT, getConfig

try:
	from lib.Core.Utils.funcs import startDaemon, stopDaemon
except ImportError as e:
	if DEBUG: print e
	from lib.Frontend.lib.Core.Utils.funcs import startDaemon, stopDaemon

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
		self.netcat_queue = []

		FileSystemEventHandler.__init__(self)

	def addToNetcatQueue(self, netcat_stub):
		if netcat_stub['save_as'] not in [ns['save_as'] for ns in self.netcat_queue]:
			self.netcat_queue.append(netcat_stub)

	def on_created(self, event):
		if event.event_type != "created" : return
		if re.match(re.compile("%s/.*" % os.path.join(ANNEX_DIR, ".git")), event.src_path) is not None: return

		filename = event.src_path.split("/")[-1]
		
		try:
			netcat_stub = [ns for ns in self.netcat_queue if ns['save_as'] == filename][0]
		except Exception as e: 
			if DEBUG: print "NO NETCAT STUB FOUND FOR %s" % filename
			return

		if DEBUG: print "NEW EVENT:\ntype: %s\nis dir: %s\npath: %s\n" % (event.event_type, event.is_directory, event.src_path)

		this_dir = os.getcwd()
		os.chdir(ANNEX_DIR)

		with settings(warn_only=True):
			# has this stub been uploaded?
			is_absorbed = local("git annex metadata %s --json --get=uv_uploaded" % filename, capture=True)
			if DEBUG: print "%s absorbed? (uv_uploaded = %s)" % (filename, is_absorbed)

			if is_absorbed == "":
				is_absorbed = False
			else:
				is_absorbed = bool(is_absorbed)

		if is_absorbed:
			if DEBUG: print "%s IS absorbed (uv_uploaded = %s)" % (filename, is_absorbed)
			return
		
		with settings(warn_only=True):
			local("git annex add %s" % filename)
			success_tag = False				

			p = UnveillanceFabricProcess(netcat, netcat_stub)
			p.join()

			if p.output is not None:
				if DEBUG: print p.output

			if p.error is None:
				success_tag = True
				self.netcat_queue.remove(netcat_stub)
			else:
				if DEBUG: print p.error

			local("git annex metadata %s --json --set=uv_uploaded=%s" % (filename, str(success_tag)))

		os.chdir(this_dir)
		sleep(5)

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
