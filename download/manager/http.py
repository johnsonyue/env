import time
import json
import BaseHTTPServer
import cgi

import manager

class Server(BaseHTTPServer.HTTPServer):
	def __init__(self, (HOST_NAME, PORT_NUMBER), handler, config):
		BaseHTTPServer.HTTPServer.__init__(self, (HOST_NAME, PORT_NUMBER), handler)
		self.config = config
	
class Handler(BaseHTTPServer.BaseHTTPRequestHandler):
	def do_HEAD(self):
		self.send_response(200)
		self.send_header("Content-type", "text/html")
		self.end_headers()
	def do_GET(self):
		"""Respond to a GET request."""
		self.send_response(200)
		self.send_header("Content-type", "text/html")
		self.end_headers()
		self.wfile.write("<html><head><title>BaseHTTPServer</title></head>")
		self.wfile.write("<body><p>It works!</p>")
		self.wfile.write("</body></html>")
	def do_POST(self):
		action = self.path.replace('/','')
		valid_action = [ "get_task", "on_notify", "auth" ]
		if ( action not in valid_action ):
			self.wfile.write("Invalid Action: %s" % action)
			return
		
		#get the config file from server.
		#note that the http request handler is not stateful.
		#however it can access the server data members.
		config = self.server.config
		log_file_name = config["manager"]["log_file_name"]
		state_file_name = config["manager"]["state_file_name"]
		secret_file_name = config["manager"]["secret_file_name"]

		post = cgi.FieldStorage(
			fp=self.rfile, 
			headers=self.headers,
			environ={'REQUEST_METHOD':'POST',
			'CONTENT_TYPE':self.headers['Content-Type'],
		})

		if ( action == "get_task" ):
			task = manager.get_task(state_file_name)
			self.wfile.write(task)
		elif ( action == "on_notify" ):
			notify_type = post["notify_type"].value
			node_id = post["node_id"].value
			task = post["task"].value
			dir = "" #optional
			if (post.has_key("dir")):
				dir = post["dir"].value
			time_used = "" #optional
			if (post.has_key("time_used")):
				time_used = post["time_used"].value
			args = {
				"node_id" : node_id,
				"task" : task,
				"dir" : dir,
				"time_used" : time_used
			}
			result = manager.on_notify(log_file_name, state_file_name, notify_type, args);
			self.wfile.write(result)
		elif ( action == "auth" ):
			node_id = post["node_id"].value
			node_key = post["node_key"].value
			result = manager.auth_node(secret_file_name, node_id, node_key);
			self.wfile.write(result)
		elif ( action == "get_path" ):
			print "SHIT"
