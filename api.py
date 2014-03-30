import os, requests, json, re
from subprocess import Popen, PIPE

from lib.Core.Utils.funcs import parseRequestEntity
from conf import BASE_DIR, buildServerURL, getUUID, DEBUG, SSH_ROOT, SERVER_HOST

class UnveillanceAPI():
	def __init__(self):
		print "Stock Unveillance Frontend API started..."
	
	def do_num_views(self, query):
		views = 0
		path = os.path.join(BASE_DIR, "web", "layout", "views", query['view_root'])
		path_e = os.path.join(BASE_DIR, "web", "extras", "layout",
			"views", query['view_root'])
			
		if DEBUG: print "GETTIN NUM VIEWS IN %s" % path
		
		for dir in [path, path_e]:			
			if os.path.exists(dir):
				for _, _, files in os.walk(dir):
					views += len(files)
					break
				
		if views != 0: return views
		else: return None
	
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
		
		"""
			1. run init_local_remote.sh
			2. get/set uuid
		"""
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
		
		"""
			3. post public key
		"""
		with open(pk_path, 'rb') as pk:
			uri = "/post_batch/%s/" % credentials['batch_root']	
			
			from vars import PostBatchStub
			post_batch = self.do_post_batch(PostBatchStub({pk_label: pk.read()}, uri))
			
			if post_batch is None: return None
		
		"""
			4. request annex to be opened on the server
			   (this returns the ports on success)
		"""
		try:
			url = "%s/init_annex/" % buildServerURL()
			if DEBUG: 
				print "now requesting annex creation on server"
				print url
				
			r = requests.post(url, data=json.dumps(credentials))
			r = json.loads(r.content)
			if DEBUG: print r
			
			if r['result'] != 200: return None
			credentials.update(r['data'])
			
		except requests.exceptions.ConnectionError as e: 
			print e
			return None
		
		"""
			5. run link_local_remote to associate local with remote annex
		"""
		cmd = [os.path.join(BASE_DIR, "link_local_remote.sh"), SSH_ROOT, 
			folder, password, SERVER_HOST, credentials['p22']]
		
		p = Popen(cmd, stdout=PIPE, close_fds=True)
		p_result = bool(p.stdout.read().strip())
		p.stdout.close()
		
		if p_result: return credentials
		return None