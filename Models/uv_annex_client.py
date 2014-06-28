from multiprocessing import Process
from apiclient import errors
from apiclient.discovery import build

from lib.Frontend.Models.uv_fabric_process import UnveillanceFabricProcess
from conf import DEBUG, getConfig, ANNEX_DIR

class UnveillanceAnnexClient(object):
	def __init__(self):
		if DEBUG: print "ANNEX CLIENT online"
		
		# get the conf settings
		try:
			self.hostname = getConfig('unveillance.local_remote.hostname')
		except KeyError as e: pass
		
		try:
			self.port = getConfig('unveillance.local_remote.port')
		except KeyError as e: pass
		
		try:
			self.user = getConfig('unveillance.local_remote.user')
		except KeyError as e: pass
		
		try:
			self.remote_path = getConfig('unveillance.local_remote.remote_path')
		except KeyError as e: pass
	
		credentials = None
		
		try:
			self.config = getSecrets(key="google_drive")
			from oauth2client.file import Storage	
			credentials = Storage(self.config['auth_storage']).get()			
		except KeyError as e:
			if DEBUG: print "NO AUTH YET!"
		
		if credentials is not None:
			http = httplib2.Http()
			http = credentials.authorize(http)
		
			self.service = build('drive', 'v2', http=http)

	def share(self, fileId, email=None):
		if not hasattr(self, "service"): return None
		if email is None: email = self.config['client_email']
		
		body = {
			'role' : "writer",
			'value' : email,
			'type' : "user"
		}
		
		try:
			return self.service.permissions().insert(fileId=fileId, body=body).execute()
		except errors.HttpError as e:
			if DEBUG: print e
		
		return None
		
	def upload(self, data, mime_type=None, as_binary=False, **body):
		if not hasattr(self, "service"): return None
		
		if not as_binary:
			try:
				with open(data, 'rb') as d: data = d.read()
			except IOError as e:
				if DEBUG: print e
				return False
		
		import io, sys
		from apiclient.http import MediaIoBaseUpload
		
		if mime_type is None:
			mime_type = "application/octet-stream"
			
		chunk_size = 1024*1024	# unless data is tiny. check first
		data = io.BytesIO(data)

		if sys.getsizeof(data) < chunk_size:
			chunk_size = -1
		
		media_body = MediaIoBaseUpload(data, mimetype=mime_type,
			chunksize=chunk_size, resumable=True)
		
		try:
			upload = self.service.files().insert(
				body=body, media_body=media_body).execute()
			
			return upload
		except errors.HttpError as e:
			if DEBUG: print e
		
		return None
	
	def getFile(self, fileId):
		if not hasattr(self, "service"): return None
		
		try:
			return self.service.files().get(fileId=fileId).execute()
		except errors.HttpError as e:
			if DEBUG: print e
		
		return None
	
	def download(self, file, save_as=None, save=True, return_content=False):
		# don't waste my time.
		if DEBUG: print "HAAAAAAAY DOWNLOAD FIRST!"
		
		if not hasattr(self, "service"): return None
		if not save and not return_content: return None
		
		if type(file) is str or type(file) is unicode:
			return self.download(self.getFile(file))
		
		url = file.get('downloadUrl')
		if url:
			content = None
			destination_path = None
			
			if save_as is None:
				save_as = self.getFileName(file)
			
			# fuck you. (path traversal)
			if len(re.findall(r'\.\.', save_as)) > 0:
				return None
			
			from conf import ANNEX_DIR
			destination_path = os.path.join(ANNEX_DIR, save_as)
			
			response, content = self.service._http.request(url)
			if response.status != 200: return None
			
			try:
				with open(destination_path, 'wb+') as C: C.write(content)
			except IOError as e:
				if DEBUG: print e
				return None
					
			if return_content: return content
			else: return destination_path
		
		return None
		
	def authenticate(self, auth_token=None):
		if auth_token is None:
			from oauth2client.client import OAuth2WebServerFlow
			
			self.flow = OAuth2WebServerFlow(
				self.config['client_id'], self.config['client_secret'],
				self.config['scopes'], 
				"http://localhost:%d%s" % (API_PORT, self.config['redirect_uri']))

			return self.flow.step1_get_authorize_url()
		else:
			credentials = self.flow.step2_exchange(auth_token)

			auth_storage = os.path.join(INFORMA_CONF_ROOT, "drive.secrets.json")
			
			from oauth2client.file import Storage
			Storage(auth_storage).put(credentials)
			
			self.config.update({
				'auth_storage' : auth_storage,
				'account_type' : "user"
			})
			
			sync_config = getSecrets(key="informacam.sync")
			sync_config['google_drive'].update(self.config)
			saveSecret("informacam.sync", sync_config)
			
			del self.flow
			return True
		
		return False