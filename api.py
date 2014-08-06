import os, requests, json, re, copy, urllib
from subprocess import Popen, PIPE
from time import sleep
from itertools import chain

from Models.uv_annex_client import UnveillanceAnnexClient
from Models.uv_fabric_process import UnveillanceFabricProcess
from Utils.fab_api import netcat
from lib.Core.vars import Result
from lib.Core.Utils.funcs import parseRequestEntity, generateMD5Hash

from conf import BASE_DIR, buildServerURL, DEBUG, SERVER_HOST, CONF_ROOT, getConfig, getSecrets, USER_ROOT

from vars import FILE_NON_OVERWRITES, USER_CREDENTIAL_PACK, UnveillanceCookie, MIME_TYPE_TASK_REQUIREMENTS

class UnveillanceAPI():
	def __init__(self):
		print "Stock Unveillance Frontend API started..."
		
		self.UNVEILLANCE_LM_VARS = {}

	def do_documents(self, handler): return self.passToAnnex(handler)

	def do_list(self, handler): return self.passToAnnex(handler)

	def do_cluster(self, handler): return self.passToAnnex(handler)
	
	def do_reindex(self, handler):
		req = parseRequestEntity(handler.request.body)
		if req is None: return None
		
		'''
			we might have to replace parts of the request with
			secret values.
		'''
		if 'task_path' in req.keys():
			req_keys = list(chain.from_iterable(
				[k.keys() for k in MIME_TYPE_TASK_REQUIREMENTS]))
					
			if req['task_path'] in req_keys:
				try:
					req_field = [k for k in MIME_TYPE_TASK_REQUIREMENTS if k.keys()[0] == req['task_path']][0][req['task_path']]
					print req_field
				except Exception as e:
					if DEBUG: print "Could not resolve required task info. %s" % e
				
				for repl in req_field.iteritems():
					if repl[0] in req.keys():				
						handler.request.body = handler.request.body.replace(
							repl[1], getSecrets(repl[1]))
									
		return self.passToAnnex(handler)
	
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
	
	def do_link_annex(self, handler):
		status = self.do_get_status(handler)
		if status != 3: return None
		
		if DEBUG:
			print "LINKING ANNEX (stock context)"
			print handler.request
		
		return None
	
	def do_open_drive_file(self, handler):
		if DEBUG: print "opening this drive file in unveillance annex"
		status = self.do_get_status(handler)
		if status not in [2,3]: 
			if DEBUG: print "NO-ACCESS TO THIS METHOD (\"do_open_drive_file\")"
			return None
		
		files = None
		
		self.initDriveClient(handler)
			
		for _id in parseRequestEntity(handler.request.query)['_ids']:
			_id = urllib.unquote(_id).replace("'", "")[1:]
			file_name = self.drive_client.getFileName(_id)

			if file_name is None: return None
			url = "%s/documents/?file_name=%s" % (buildServerURL(), file_name)

			entry = None
			handled_file = None
		
			if DEBUG: print url
			
			# look up the file in annex. (annex/documents/?file_name=file)
			# if this file exists in annex, return its _id for opening in-app
			try:
				entry = json.loads(requests.get(
					url, verify=False).content)['data']['documents'][0]
			except Exception as e:
				if DEBUG: print "COULD NOT GET ENTRY:\n%s" % e
			
			if entry is not None:
				if DEBUG: print type(entry['_id'])
				handled_file = { '_id' : entry['_id'] }
			else:
				if status != 3:
					if DEBUG:
						print "** at this point, we would process file if you were admin"
						print "** but you are not admin."
					
					return None
						
				entry = self.drive_client.download(_id, 
					save_as=file_name, save=False, return_content=True)

				if entry is not None:
					p = UnveillanceFabricProcess(netcat, {
						'file' : entry[0],
						'save_as' : entry[1]
					})
					p.join()
		
					if p.output is not None:
						if DEBUG: print p.output
						handled_file = { 'file_name' : entry[1] }
				
					if DEBUG and p.error is not None: print p.error
			
			if handled_file is not None:
				if files is None: files = []
				files.append(handled_file)
		
		return files
	
	def do_get_admin_party_status(self, handler):
		status = self.do_get_status(handler)
		if status == 0: return None
		
		from conf import USER_ROOT
		for _, _, files in os.walk(USER_ROOT):
			for f in files: return False
		
		return True

	def do_create_new_user(self, handler):
		status = self.do_get_status(handler)

		if status != 3: return None

		new_user = parseRequestEntity(handler.request.body)
		if new_user is None: return None
		if DEBUG: print new_user

		n_set = sorted(['nu_username', 'nu_password'])
		if sorted(list(set(n_set) & set(new_user.keys()))) != n_set:
			return None

		from Utils.funcs import createNewUser
		return createNewUser(new_user['nu_username'], new_user['nu_password'])
	
	def do_get_user_status(self, handler):
		status = self.do_get_status(handler)

		if status == 0: return None		
		if self.do_get_admin_party_status(handler): return 4
		
		return status
		
	def do_get_status(self, handler):
		try:
			for cookie in handler.request.cookies:
				if cookie == UnveillanceCookie.PUBLIC: return 0
		except KeyError as e: pass
		
		access = handler.get_secure_cookie(UnveillanceCookie.USER)
		if access is not None:
			if handler.get_secure_cookie(UnveillanceCookie.ADMIN) is not None:
				return 3
				
			return 2

		return 1
	
	def do_get_drive_status(self, handler=None):
		if handler is not None:
			if self.do_get_status(handler) == 0: return None
			# TODO: actually, if not 3

		if hasattr(self, "drive_client"):
			if hasattr(self.drive_client, "service"):
				return True

		return False
		
	def do_logout(self, handler):
		status = self.do_get_status(handler)
		if status not in [2, 3]:
			if DEBUG: print "CANNOT LOG IN USER, DON'T EVEN TRY (status %d)" % status
			return None
				
		credentials = parseRequestEntity(handler.request.body)
		if credentials is None: return None
		if DEBUG: print credentials
		
		return self.logoutUser(credentials, handler)
	
	def do_login(self, handler):
		status = self.do_get_status(handler)
		if status != 1:
			if DEBUG: print "CANNOT LOG IN USER, DON'T EVEN TRY (status %d)" % status
			return None
		
		credentials = parseRequestEntity(handler.request.body)
		if credentials is None: return None
		if DEBUG: print credentials
		
		try:	
			return self.loginUser(credentials['username'], 
				credentials['password'], handler)
		except KeyError as e:
			if DEBUG: print "CANNOT LOG IN USER: %s missing" % e
			return None
			
	def initDriveClient(self, restart=False):
		if DEBUG: print "INITING DRIVE CLIENT"		
		if not hasattr(self, "drive_client") or restart:
			self.drive_client = UnveillanceAnnexClient()
			sleep(2)

		return self.do_get_drive_status()
	
	def logoutUser(self, credentials, handler):
		handler.clear_cookie(UnveillanceCookie.USER)
		handler.clear_cookie(UnveillanceCookie.ADMIN)
		
		try:
			username = credentials['username']
		except KeyError as e: return None
		
		try:
			password = credentials['password']
		except KeyError as e: return True
		
		try:
			IV = getConfig('encryption.iv')
			SALT = getConfig('encryption.salt')
			USER_SALT = getConfig('encyption.user_salt')
		except Exception as e:
			if DEBUG: print e
			return None		
		
		try:
			from Utils.funcs import decryptUserData, encryptUserData
		except Exception as e:
			if DEBUG: print e
			from lib.Frontend.Utils.funcs import decryptUserData, encryptUserData
				
		user_root = "%s.txt" % generateMD5Hash(content=username,salt=USER_SALT)
		with open(os.path.join(USER_ROOT, user_root), 'rb') as UD:
			user_data = decryptUserData(UD.read, password, p_salt=SALT)
			
			if user_data is None: return None
			
			new_data = copy.deepcopy(user_data)
			new_data['saved_searches'] = credentials['save_data']['saved_searches']
			try:
				new_data['annex_key_sent'] = credentials['save_data']['annex_key_sent']
			except KeyError as e:
				pass
		
		with open(os.path.join(USER_ROOT, user_root), 'wb+') as UD:
			UD.write(encryptUserData(new_data, password, iv=IV, p_salt=SALT))
			return True
		
		return None
	
	def loginUser(self, username, password, handler):
		try:
			SALT = getConfig('encryption.salt')
			USER_SALT = getConfig('encyption.user_salt')
		except Exception as e:
			if DEBUG: print e
			return None		
		
		from base64 import b64encode
		try:
			from Utils.funcs import decryptUserData
		except Exception as e:
			if DEBUG: print e
			from lib.Frontend.Utils.funcs import decryptUserData

		try:
			user_root = "%s.txt" % generateMD5Hash(content=username, salt=USER_SALT)
			with open(os.path.join(USER_ROOT, user_root), 'rb') as UD:
				user_data = decryptUserData(UD.read(), password, p_salt=SALT)
				if user_data is None: return None
				
				try:
					if user_data['admin']:
						del user_data['admin']
						handler.set_secure_cookie(UnveillanceCookie.ADMIN, 
							"true", path="/", expires_days=1)
							
						if not self.do_get_drive_status():
							self.initDriveClient()
							if "annex_key_sent" not in user_data.keys() or not user_data['annex_key_sent']:							
								if self.drive_client.checkAnnexKeyStatus():
									user_data['annex_key_sent'] = True

				except KeyError as e: 
					if DEBUG: print e
					pass
				
				handler.set_secure_cookie(UnveillanceCookie.USER, 
					b64encode(json.dumps(user_data)), path="/", expires_days=1)
				
				return user_data
		
		except Exception as e:
			if DEBUG: print e		
		
		return None