import os, re
from time import sleep

from fabric.api import settings, local

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from conf import DEBUG, ANNEX_DIR, MONITOR_ROOT, GIT_ANNEX, getConfig

try:
	from lib.Core.Utils.funcs import startDaemon, stopDaemon, generateMD5Hash
except ImportError as e:
	if DEBUG: print e
	from lib.Frontend.lib.Core.Utils.funcs import startDaemon, stopDaemon, generateMD5Hash

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

	def addToNetcatQueue(self, netcat_stub, send_now=True):
		if netcat_stub['save_as'] not in [ns['save_as'] for ns in self.netcat_queue]:
			self.netcat_queue.append(netcat_stub)

			if(send_now): self.uploadToAnnex(netcat_stub)

	def uploadToAnnex(self, netcat_stub):
		this_dir = os.getcwd()
		os.chdir(ANNEX_DIR)

		with settings(warn_only=True):
			# has this stub been uploaded?
			is_absorbed = local("%s metadata \"%s\" --json --get=uv_uploaded" % (
				GIT_ANNEX, netcat_stub['save_as']), capture=True)

			if DEBUG: print "%s absorbed? (uv_uploaded = %s type = %s)" % (
				netcat_stub['save_as'], is_absorbed, type(is_absorbed))

			if is_absorbed == "" or "False": is_absorbed = False
			elif is_absorbed == "True": is_absorbed = True
			else: is_absorbed = False

		if is_absorbed:
			if DEBUG: print "%s IS absorbed (uv_uploaded = %s)" % (
				netcat_stub['save_as'], is_absorbed)
			
			os.chdir(this_dir)
			return

		with settings(warn_only=True):
			new_save_as = generateMD5Hash(content=netcat_stub['save_as'], salt=local("whoami", capture=True))
		
		print "NETCAT FILE TYPE: %s" % type(netcat_stub['file'])

		if type(netcat_stub['file']) in [str, unicode]:
			new_file = netcat_stub['file'].replace(netcat_stub['save_as'], new_save_as)

			with settings(warn_only=True):
				local("mv \"%s\" %s" % (netcat_stub['file'], new_file))

			netcat_stub['file'] = new_file

		netcat_stub['alias'] = netcat_stub['save_as']
		netcat_stub['save_as'] = new_save_as

		with settings(warn_only=True):
			if type(netcat_stub['file']) in [str, unicode]:
				local("%s add %s" % (GIT_ANNEX, netcat_stub['save_as']))
			
			success_tag = False				

			p = UnveillanceFabricProcess(netcat, netcat_stub)
			p.join()

			if p.error is None and p.output is not None: success_tag = True

			if DEBUG: print "NETCAT RESULT: (type=%s, success=%s)" % (type(p.output), success_tag)
			if DEBUG: print "NETCAT ERROR (none is good!): (type=%s)" % type(p.error)

			if DEBUG and p.output is not None:
				for o in p.output: print "\n%s\n" % o

			if p.error is not None and DEBUG:
				print "ERROR:"
				print p.error

			if type(netcat_stub['file']) in [str, unicode]:
				local("%s metadata \"%s\" --json --set=uv_uploaded=%s" % (
					GIT_ANNEX, netcat_stub['save_as'], str(success_tag)))

			if success_tag: self.netcat_queue.remove(netcat_stub)

		os.chdir(this_dir)


	def on_created(self, event):
		if event.event_type != "created" : return
		if re.match(re.compile("%s/.*" % os.path.join(ANNEX_DIR, ".git")), event.src_path) is not None: return

		filename = event.src_path.split("/")[-1]
		netcat_stub = None

		try:
			netcat_stub = [ns for ns in self.netcat_queue if ns['save_as'] == filename][0]
		except Exception as e: 
			if DEBUG: print "NO NETCAT STUB FOUND FOR %s" % filename

		if DEBUG: print "NEW EVENT:\ntype: %s\nis dir: %s\npath: %s\n" % (event.event_type, event.is_directory, event.src_path)

		if netcat_stub is None:
			netcat_stub = {
				'file' : event.src_path,
				'save_as' : filename,
				'importer_source' : "file_added"
			}

			self.addToNetcatQueue(netcat_stub)

		sleep(5)

	def startAnnexObserver(self):
		print "STARTING OBSERVER on %s" % ANNEX_DIR

		startDaemon(self.watcher_log_file, self.watcher_pid_file)
		self.annex_observer.schedule(self, ANNEX_DIR, recursive=True)
		self.annex_observer.start()
		
		while True: sleep(1)

	def stopAnnexObserver(self):
		print "STOPPING OBSERVER"
		self.annex_observer.stop()
		self.annex_observer.join()

		stopDaemon(self.watcher_pid_file)
