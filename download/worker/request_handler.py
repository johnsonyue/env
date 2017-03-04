import urllib
import urllib2
import json

class RequestHandler():
	def __init__(self, config_file_name):
		self.config = json.loads(open(config_file_name,'rb').read())

		site = self.config["worker"]["site"]
		get_task = self.config["worker"]["get_task"]
		self.get_task_url = "%s/%s" % (site, get_task)

		on_notify = self.config["worker"]["on_notify"]
		self.notify_url = "%s/%s" % (site, on_notify)

		self.node_id = self.config["worker"]["node"]["node_id"]
		self.node_key = self.config["worker"]["node"]["node_key"]

	def get_task(self, source):
		params = { "node_id": self.node_id, "node_key": self.node_key, "source": source}; 
		opener = urllib2.build_opener()
		post_data = urllib.urlencode(params).encode('utf-8')
		res = opener.open(self.get_task_url, post_data).read()
		if (res == "auth failed"):
			print "auth failed"
			exit()
	
		return res
	
	def notify_started(self, date, source):
		params = { "node_id": self.node_id, "node_key": self.node_key, "notify_type": "started", "task": date , "source": source}
		opener = urllib2.build_opener()
		post_data = urllib.urlencode(params).encode('utf-8')
		res = opener.open(self.notify_url, post_data).read()
		if (res == "auth failed"):
			print "auth failed"
			exit()
						
		return res
	
	def notify_finished(self, date, time_used, source):
		params = { "node_id": self.node_id, "node_key": self.node_key , "notify_type": "finished", "task" : date, "time_used": time_used , "source": source}
		opener = urllib2.build_opener()
		post_data = urllib.urlencode(params).encode('utf-8')
		res = opener.open(self.notify_url, post_data).read()
		if (res == "auth failed"):
			print "auth failed"
			exit()
		
		return res

	def notify_terminated(self, date, source):
		params = { "node_id": self.node_id, "node_key": self.node_key , "notify_type": "terminated", "task": date , "source": source}
		opener = urllib2.build_opener()
		post_data = urllib.urlencode(params).encode('utf-8')
		res = opener.open(self.notify_url, post_data).read()
		if (res == "auth failed"):
			print "auth failed"
			exit()
		
		return res
