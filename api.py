import os, requests, json

from lib.Core.Utils.funcs import parseRequestEntity
from conf import BASE_DIR, buildServerURL, getUUID, DEBUG

class UnveillanceAPI():
	def __init__(self):
		print "Stock Unveillance Frontend API started..."
	
	def do_num_views(self, query):
		path = os.path.join(BASE_DIR, "web", "layout", "views", query['view_root'])
		if DEBUG: print "GETTIN NUM VIEWS IN %s" % path
		
		if os.path.exists(path):
			for _, _, files in os.walk(path): return len(files)
				
		return None
	
	def do_post_batch(self, request):
		# just bouce request to server/post_batch/tmp_id
		url = "%s%s" % (buildServerURL(), request.uri)

		if DEBUG:
			print "POST BATCH"
			print request.files
			print url
		
		try:
			r = requests.post(url, files=request.files)
			if DEBUG:
				print "BOUNCE:"
				print r.content
			
			return json.loads(r.content)
	
		except requests.exceptions.ConnectionError as e: print e
		return None
	
	def do_init_annex(self, request):
		if DEBUG:
			print "INIT ANNEX (Stock Context)"
			print request
		
		credentials = parseRequestEntity(request.body)
		if DEBUG: print credentials
		if credentials is None: return None
		
		from subprocess import Popen
		from conf import SSH_ROOT
		
		try:
			if DEBUG: print "initing annex script"
			
			password = credentials['unveillance.local_remote.password']
			del credentials['unveillance.local_remote.password']
			
			folder = credentials['unveillance.local_remote.folder']
			del credentials['unveillance.local_remote.folder']
					
			p = Popen([os.path.join(BASE_DIR, "init_local_remote.sh"), 
				SSH_ROOT, folder, password])
			p.wait()
		
			pk_label = "unveillance.local_remote.key.pub"
			pk_path = os.path.join(SSH_ROOT, pk_label)
			
			credentials['uuid'] = getUUID()
		
		except Exception as e: 
			print e
			return None
		
		with open(pk_path, 'rb') as pk:
			uri = "/post_batch/%s/" % credentials['batch_root']	
			
			from vars import PostBatchStub
			post_batch = self.do_post_batch(PostBatchStub({pk_label: pk.read()}, uri))
			
			if post_batch is None: return None
		
		return credentials