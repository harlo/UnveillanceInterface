import json, signal, os, logging
from sys import exit, argv
from multiprocessing import Process
from time import sleep

import tornado.ioloop
import tornado.web
import tornado.httpserver

from api import UnveillanceAPI
from lib.Core.Utils.uv_result import Result
from lib.Core.Utils.funcs import startDaemon, stopDaemon
from conf import MONIOR_ROOT, BASE_DIR, API_PORT, NUM_PROCESSES

def terminationHandler(signal, frame): exit(0)
signal.signal(signal.SIGINT, terminationHandler)

class UnveillanceFrontend(tornado.web.Application, UnveillanceAPI):
	def __init__(self):
		self.api_pid_file = os.path.join(MONITOR_ROOT, "frontend.pid.txt")
		self.api_log_file = os.path.join(MONITOR_ROOT, "frontend.log.txt")
		
		self.routes = [
			(r"/(?:(?!web/|externals/))([a-zA-Z0-9_/]*/$)?", 
				self.RouteHandler, dict(route=None)),
			(r"/web/([a-zA-Z0-9\-\._]+)", tornado.web.StaticFileHandler,
				{"path" : os.path.join(BASE_DIR, "web")})]
		
		self.on_loads = {
			'annex_admin' : [
				"/web/js/lib/md5.js",
				"/web/js/models/unveillance_annex.js",
				"/web/js/models/informa_annex.js",
				"/web/js/modules/init_annex.js",
				"/web/js/lib/dropzone.js",
				"/web/js/models/unveillance_dropzone.js"
			]
		}
	
		class RouteHandler(tornado.web.RequestHandler):
			def initialize(self, route): 
				self.route = route
		
			@tornado.web.asynchronous
			def get(self, route):
				static_path = os.path.join(BASE_DIR, "web")
				content = None
				r = "main"
			
				if route is None:
					idx = Template(filename=os.path.join(static_path, "index.html"))
				else:
					route = [r_ for r_ in route.split("/") if r_ != '']
					r = route[0]
					print r
				
					idx = Template(filename=os.path.join(static_path, "module.html"))
					content = Template(filename=os.path.join(
						static_path, "layout", "%s.html" % r)).render()
			
				self.finish(idx.render(on_loader=self.getOnLoad(r), content=content))
		
			def getOnLoad(self, route):
				js = '<script type="text/javascript" src="%s"></script>'
				if route in [k for k,v in self.on_loads.iteritems()]:
					return "".join([js % v for v in self.on_loads[route]])

				return ""
		
			@tornado.web.asynchronous
			def post(self, route):
				res = Result()
			
				if route is not None:
					route = [r_ for r_ in route.split("/") if r_ != '']
					r = "do_%s" % route[0]
				
					if hasattr(self.application, r):
						print "doing %s with:\n" % r
						res.result = 200
	
						func = getattr(self.application, r)
						if len(self.request.body) > 0:
							if not passesParameterFilter(self.request.body):
								res.result = 404
							
								self.set_status(res.result)
								self.finish(res.emit())
								return
							
							print self.request.body				
							res.data = func(json.loads(self.request.body))
						else: res.data = func()
					
						if res.data is None: res.data = {}
			
				self.set_status(res.result)					
				self.finish(res.emit())
		
	def startup(self):
		p = Process(target=self.startRESTAPI)
		p.start()
		
	def shutdown(self):
		self.stopRESTAPI()
	
	def startRESTAPI(self):
		#startDaemon(self.api_log_file, self.api_pid_file)

		tornado.web.Application.__init__(self, self.routes)
		
		server = tornado.httpserver.HTTPServer(self)
		server.bind(API_PORT)
		server.start(NUM_PROCESSES)
		
		tornado.ioloop.IOLoop.instance().start()
	
	def stopRESTAPI(self):
		print "shutting down REST API"
		stopDaemon(self.api_pid_file, extra_pids_port=API_PORT)