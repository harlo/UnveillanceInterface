import json, signal, os, logging
from sys import exit, argv
from multiprocessing import Process
from time import sleep

import tornado.ioloop
import tornado.web
import tornado.httpserver
from mako.template import Template

from api import UnveillanceAPI
from lib.Core.Utils.uv_result import Result
from lib.Core.Utils.funcs import startDaemon, stopDaemon, parseRequestEntity
from conf import MONITOR_ROOT, BASE_DIR, API_PORT, NUM_PROCESSES
from conf import DEBUG

def terminationHandler(signal, frame): exit(0)
signal.signal(signal.SIGINT, terminationHandler)

class UnveillanceFrontend(tornado.web.Application, UnveillanceAPI):
	def __init__(self):
		self.api_pid_file = os.path.join(MONITOR_ROOT, "frontend.pid.txt")
		self.api_log_file = os.path.join(MONITOR_ROOT, "frontend.log.txt")
		
		self.reserved_routes = ["frontend", "web", "setup"]
		self.routes = [
			(r"/frontend/", self.FrontendHandler),
			(r"/(?:(?!web/|frontend/))([a-zA-Z0-9_/]*/$)?", self.RouteHandler),
			(r"/web/([a-zA-Z0-9\-\._/]+)", tornado.web.StaticFileHandler,
				{"path" : os.path.join(BASE_DIR, "web")})]
		
		self.on_loads = {
			'setup' : [
				"/web/js/lib/sammy.js",
				"/web/js/lib/md5.js",
				"/web/js/models/unveillance_annex.js",
				"/web/js/modules/setup.js",
				"/web/js/lib/dropzone.js",
				"/web/js/models/unveillance_dropzone.js"
			]
		}
		
		UnveillanceAPI.__init__(self)
		
	class FrontendHandler(tornado.web.RequestHandler):
		@tornado.web.asynchronous
		def get(self):
			res = Result()
			query = parseRequestEntity(self.request.query)
			
			if DEBUG : 
				print self.request.query
				print query
			
			if query is not None:
				try:
					r = query['req']
					del query['req']
					
					res = self.application.routeRequest(res, r, query)
				except KeyError as e: print e				
				
			self.set_status(res.result)
			self.finish(res.emit())
		
	class RouteHandler(tornado.web.RequestHandler):	
		@tornado.web.asynchronous
		def get(self, route):
			static_path = os.path.join(BASE_DIR, "web")			
			r = "main"
		
			if route is None:
				idx = Template(filename=os.path.join(static_path, "index.html"))
			else:
				route = [r_ for r_ in route.split("/") if r_ != '']
				r = route[0]				
			
				idx = Template(filename=os.path.join(static_path, "module.html"))
			
			layout = os.path.join(static_path, "layout", "%s.html" % r)
			
			if DEBUG : print (r, layout)
				
			if not os.path.exists(layout):
				# try the externals...
				layout = os.path.join(static_path, "extras", "layout", "%s.html" % r)
				
			if not os.path.exists(layout):
				res = Result()
				
				self.set_status(res.result)
				self.finish(res.emit())
				return

			content = Template(filename=layout).render()
			self.finish(idx.render(on_loader=self.getOnLoad(r), content=content))
	
		def getOnLoad(self, route):
			js = '<script type="text/javascript" src="%s"></script>'
			if route in [k for k,v in self.application.on_loads.iteritems()]:
				if DEBUG : print self.application.on_loads[route]
				return "".join([js % v for v in self.application.on_loads[route]])

			return ""
	
		@tornado.web.asynchronous
		def post(self, route):
			res = Result()
		
			if route is not None:
				route = [r_ for r_ in route.split("/") if r_ != '']
				res = self.application.routeRequest(res, route[0], self.request)
			
			if DEBUG : print res.emit()
			
			self.set_status(res.result)					
			self.finish(res.emit())
	
	def routeRequest(self, result_obj, func_name, request):
		func_name = "do_%s" % func_name
		if hasattr(self, func_name):
			if DEBUG : print "doing %s" % func_name
			func = getattr(self, func_name)
			
			result_obj.result = 200
			result_obj.data = func(request)
		else:
			if DEBUG : print "could not find function %s" % func_name

		if result_obj.data is None: 
			del result_obj.data
			result_obj.result = 412

		return result_obj
	
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
		if DEBUG : print "shutting down REST API"
		stopDaemon(self.api_pid_file, extra_pids_port=API_PORT)

if __name__ == "__main__":
	unveillance_frontend = UnveillanceFrontend()
	
	if len(argv) != 2: exit("Usage: unveillance_frontend.py [-start, -stop, -restart]")
	
	if argv[1] == "-start" or argv[1] == "-firstuse":
		unveillance_frontend.startup()
	elif argv[1] == "-stop":
		unveillance_frontend.shutdown()
	elif argv[1] == "-restart":
		unveillance_frontend.shutdown()
		sleep(5)
		unveillance_frontend.startup()