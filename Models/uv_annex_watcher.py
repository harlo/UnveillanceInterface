import os, re
from time import sleep

from fabric.api import settings, local

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from conf import DEBUG, ANNEX_DIR, getConfig

try:
	from Models.uv_fabric_process import UnveillanceFabricProcess
except ImportError as e:
	if DEBUG: print e
	from lib.Frontend.Models.uv_fabric_process import UnveillanceFabricProcess

class UnveillanceFSEHandler(FileSystemEventHandler):
	def __init__(self, path):
		self.path = path
		self.observer = Observer()

		FileSystemEventHandler.__init__(self)

	def on_created(self, event):
		if event.event_type != "created" : return
		if re.match(re.compile("%s/.*" % os.path.join(self.path, ".git")), event.src_path) is not None: return

		if DEBUG: print "NEW EVENT:\ntype: %s\nis dir: %s\npath: %s\n" % (event.event_type, event.is_directory, event.src_path)

		filename = event.src_path.split("/")[-1]

		this_dir = os.getcwd()
		os.chdir(ANNEX_DIR)
		
		with settings(warn_only=True):
			local("%s add %s" % (getConfig('git_annex_dir'), filename))
			success_tag = False

			p = UnveillanceFabricProcess(netcat, {
				'file' : event.src_path,
				'save_as' : filename
			})
			p.join()

			if p.output is not None:
				if DEBUG: print p.output

			if p.error is None:
				success_tag = True
			else:
				if DEBUG: print p.error

			local("%s metadata --tag uv_uploaded_%s %s" % (getConfig('git_annex_dir'), str(success_flag), filename))
	
		os.chdir(this_dir)

	def start(self):
		self.observer.schedule(self, self.path, recursive=True)
		print "STARTING OBSERVER on %s" % self.path
		self.observer.start()

		while True:
			sleep(1)

	def stop(self):
		print "STOPPING OBSERVER"
		self.observer.stop()
		self.observer.join()
