import json, signal, os, logging, re, webbrowser, requests
from sys import exit, argv
from multiprocessing import Process
from time import sleep

import tornado.ioloop
import tornado.web
import tornado.httpserver
from mako.template import Template

from api import UnveillanceAPI
from lib.Core.vars import Result
from lib.Core.Utils.funcs import startDaemon, stopDaemon, parseRequestEntity

from conf import MONITOR_ROOT, BASE_DIR, API_PORT, NUM_PROCESSES, WEB_TITLE, UV_COOKIE_SECRET, buildServerURL, buildRemoteURL
from conf import DEBUG

def terminationHandler(signal, frame): exit(0)
signal.signal(signal.SIGINT, terminationHandler)

class UnveillanceFrontend(tornado.web.Application, UnveillanceAPI):
	def __init__(self):
		self.api_pid_file = os.path.join(MONITOR_ROOT, "frontend.pid.txt")
		self.api_log_file = os.path.join(MONITOR_ROOT, "frontend.log.txt")
		
		self.taskman_pid_file = os.path.join(MONITOR_ROOT, "taskman.pid.txt")
		self.taskman_log_file = os.path.join(MONITOR_ROOT, "taskman.log.txt")
		
		self.reserved_routes = ["frontend", "web", "files"]
		self.routes = [
			(r"/frontend/", self.FrontendHandler),
			(r"/web/([a-zA-Z0-9\-\._/]+)", self.WebAssetHandler),
			(r"/cdn/([a-zA-Z0-9\-\._/]+)", self.CDNHandler),
			(r"/files/(.+)", self.FileHandler)]
		
		self.on_loads = {
			'setup' : [
				"/web/js/lib/sammy.js",
				"/web/js/lib/md5.js",
				"/web/js/models/unveillance_annex.js",
				"/web/js/handlers/uv_annex_listener.js",
				"/web/js/modules/setup.js",
				"/web/js/lib/dropzone.js",
				"/web/js/models/unveillance_dropzone.js"
			],
			'collaboration' : [
				"/web/js/lib/sammy.js",
				"/web/js/modules/collaboration.js"
			],
			'sync' : [
				"/web/js/lib/sammy.js",
				"/web/js/lib/dropzone.js",
				"/web/js/lib/md5.js",
				"/web/js/models/unveillance_dropzone.js",
				"/web/js/models/unveillance_synctask.js",
				"/web/js/modules/sync.js",
			]
		}
		
		UnveillanceAPI.__init__(self)
	
	class CDNHandler(tornado.web.RequestHandler):
		@tornado.web.asynchronous
		def get(self, uri):
			r = requests.get("https://%s" % uri)
			
			try:
				self.set_status(r.status_code)
				self.finish(r.content)

				return

			except Exception as e:
				if DEBUG: print e
				
			res = Result()
			self.set_status(res.status)
			self.finish(res.emit())
	
	class WebAssetHandler(tornado.web.RequestHandler):	# TODO: secure this better.
		@tornado.web.asynchronous
		def get(self, uri):
			if uri == "conf.json":
				if hasattr(self.application, "init_vars"):
					init_vars = self.application.init_vars
				else: init_vars = {}
					
				self.finish(json.dumps(init_vars))
				return
			
			static_path = os.path.join(BASE_DIR, "web")
			asset = os.path.join(static_path, uri)
			
			if not os.path.exists(asset):
				asset = os.path.join(static_path, "extras", uri)
			
			if not os.path.exists(asset):
				res = Result()
				
				self.set_status(res.result)
				self.finish(res.emit())
				return
			
			with open(asset, 'rb') as a: self.finish(a.read())
				
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
	
	class FileHandler(tornado.web.RequestHandler):
		@tornado.web.asynchronous
		def get(self, file):
			url = "%s%s" % (buildRemoteURL(), self.request.uri)
			if DEBUG: print url
			
			r = requests.get(url)
			self.finish(r.content)
		
	class RouteHandler(tornado.web.RequestHandler):	
		@tornado.web.asynchronous
		def get(self, route):
			static_path = os.path.join(BASE_DIR, "web")
			module = "main"
			header = None
			footer = None

			if hasattr(self.application, "WEB_TITLE"): 
				web_title = self.application.WEB_TITLE
			else: web_title = WEB_TITLE
		
			if route is None:
				if hasattr(self.application, "INDEX_HEADER"):
					header = self.application.INDEX_HEADER
				if hasattr(self.application, "INDEX_FOOTER"):
					footer = self.application.INDEX_FOOTER
				
				idx = Template(filename=os.path.join(static_path, "index.html"))
					
			else:
				route = [r for r in route.split("/") if r != '']
				module = route[0]
				if hasattr(self.application, "MODULE_HEADER"):
					header = self.application.MODULE_HEADER
				if hasattr(self.application, "MODULE_FOOTER"):
					footer = self.application.MODULE_FOOTER
			
				idx = Template(filename=os.path.join(static_path, "module.html"))
				web_title = "%s : %s" % (web_title, module)
			
			layout = os.path.join(static_path, "layout", "%s.html" % module)
			
			if DEBUG : print (module, layout)
				
			if not os.path.exists(layout):
				# try the externals...
				layout = os.path.join(static_path, "extras", "layout", "%s.html" % module)
				if DEBUG: 
					print "could not find layout at web root.  trying externals:"
					print layout
				
			if not os.path.exists(layout):
				res = Result()
				
				self.set_status(res.result)
				self.finish(res.emit())
				return

			content = Template(filename=layout).render()

			if header is not None: header = Template(filename=header).render()
			else: header = ""
			
			if footer is not None: footer = Template(filename=footer).render()
			else: footer = ""
			
			self.finish(idx.render(web_title=web_title, on_loader=self.getOnLoad(module),
				content=content, header=header, footer=footer))
	
		def getOnLoad(self, module):
			on_loads = []
			if hasattr(self.application, "default_on_loads"):
				on_loads.extend(self.application.default_on_loads)
				
			js = '<script type="text/javascript" src="%s"></script>'
			if module in [k for k,v in self.application.on_loads.iteritems()]:
				on_loads.extend(self.application.on_loads[module])
			
			if DEBUG: print "ALL ON_LOADS\n%s" % on_loads
			return "".join([js % v for v in on_loads])

		@tornado.web.asynchronous
		def post(self, route):
			res = Result()
		
			if route is not None:
				route = [r_ for r_ in route.split("/") if r_ != '']
				res = self.application.routeRequest(res, route[0], self)
						
			self.set_status(res.result)					
			self.finish(res.emit())
	
	def passToAnnex(self, handler):
		if handler.request.body != None:
			ref = "?%s" % handler.request.body
		else:
			ref = handler.request.headers['Referer']
		query = ""
		try:
			query += ref[ref.index("?"):]
		except ValueError as e: pass

		url = "%s%s%s" % (buildServerURL(), handler.request.uri, query)

		if DEBUG: print "SENDING REQUEST TO %s" % url
		r = requests.get(url)
		
		try:
			return json.loads(r.content)['data']
		except Exception as e:
			if DEBUG: print e
		
		return None

	def routeRequest(self, result_obj, func_name, handler):
		func_name = "do_%s" % func_name
		if hasattr(self, func_name):
			if DEBUG : print "doing %s" % func_name
			func = getattr(self, func_name)
			
			result_obj.result = 200
			result_obj.data = func(handler)
		else:
			if DEBUG : print "could not find function %s" % func_name
		
		try:
			if result_obj.data is None: 
				del result_obj.data
				result_obj.result = 412
		except AttributeError as e: pass

		return result_obj
	
	def startup(self, openurl=False):
		p = Process(target=self.startTaskMan)
		p.start()
		
		p = Process(target=self.startRESTAPI)
		p.start()
		
		if openurl:
			url = "http://localhost:%d/" % API_PORT
			if argv[1] == "-firstuse": url += "setup/"
			webbrowser.open(url)
		
	def shutdown(self):
		self.stopRESTAPI()
		self.stopTaskMan()
	
	def startTaskMan(self):
		if DEBUG : print "starting up TASK_MAN"
		startDaemon(self.taskman_log_file, self.taskman_pid_file)
		
		while True: sleep(1)		
	
	def stopTaskMan(self):
		if DEBUG : print "shutting down TASK_MAN"
		stopDaemon(self.taskman_pid_file)
	
	def startRESTAPI(self):
		#startDaemon(self.api_log_file, self.api_pid_file)
		
		rr_group = r"/(?:(?!%s))([a-zA-Z0-9_/]*/$)?" % "|".join(self.reserved_routes)
		self.routes.append((re.compile(rr_group).pattern, self.RouteHandler))
		tornado.web.Application.__init__(self, self.routes,
			**{'cookie_secret' : UV_COOKIE_SECRET })
		
		server = tornado.httpserver.HTTPServer(self)
		server.bind(API_PORT)
		server.start(NUM_PROCESSES)
		
		tornado.ioloop.IOLoop.instance().start()
	
	def stopRESTAPI(self):
		if DEBUG : print "shutting down REST API"
		stopDaemon(self.api_pid_file, extra_pids_port=API_PORT)

if __name__ == "__main__":
	unveillance_frontend = UnveillanceFrontend()
	
	openurl = False
	
	if len(argv) == 3 and argv[2] == "-webapp":
		openurl = True
		arvg.pop()
		
	if len(argv) != 2: exit("Usage: unveillance_frontend.py [-start, -stop, -restart]")
	
	if argv[1] == "-start" or argv[1] == "-firstuse":
		unveillance_frontend.startup()
	elif argv[1] == "-stop":
		unveillance_frontend.shutdown()
	elif argv[1] == "-restart":
		unveillance_frontend.shutdown()
		sleep(5)
		unveillance_frontend.startup(openurl)