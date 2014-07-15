from lib.Core.vars import *
from collections import namedtuple

PostBatchRequestStub = namedtuple("PostBatchRequestStub", "files uri")
class PostBatchStub(object):
	def __init__(self, files, uri):
		self.request = PostBatchRequestStub(files, uri)

unveillance_cookie = namedtuple("unveillance_cookie", "ADMIN USER PUBLIC")
UnveillanceCookie = unveillance_cookie("uv_admin", "uv_user", "uv_public")

FILE_NON_OVERWRITES = []

USER_CREDENTIAL_PACK = {
	"username" : "",
	"saved_searches" : [],
	"session_log" : []
}

MIME_TYPES = {
	'txt' : "text/plain",
	'zip' : "application/zip",
	'image' : "image/jpeg",
	'wildcard' : "application/octet-stream",
	'pgp' : "application/pgp",
	'gzip' : "application/x-gzip",
	'json' : "application/json"
}

MIME_TYPE_MAP = {
	'text/plain' : "txt",
	'application/zip' : "zip",
	'image/jpeg' : "jpg",
	'application/octet-stream' : "wildcard",
	'application/pgp' : "pgp",
	'application/x-gzip' : "gzip",
	'application/json' : "json"
}

MIME_TYPE_TASK_REQUIREMENTS = []