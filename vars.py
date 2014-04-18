from lib.Core.vars import *
from collections import namedtuple

PostBatchRequestStub = namedtuple("PostBatchRequestStub", "files uri")

class PostBatchStub(object):
	def __init__(self, files, uri):
		self.request = PostBatchRequestStub(files, uri)

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