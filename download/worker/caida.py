import HTMLParser
import urllib2
import re
import os
import json
import time

import multi_thread

#load authentication info.
def load_auth(auth_file):
	j = json.loads( open(auth_file,'r').read() )
	return { "username":j["caida"]["username"], "password":j["caida"]["password"] }
		
#html parsers.
class CaidaParser(HTMLParser.HTMLParser):
	def __init__(self):
		HTMLParser.HTMLParser.__init__(self)
		self.img_cnt=0
		self.alt=""
		self.file=[]
		self.dir=[]

	def get_attr_value(self, target, attrs):
		for e in attrs:
			key = e[0]
			value = e[1]
			if (key == target):
				return value

	def handle_starttag(self, tag, attrs):
		if (tag == "img"):
			if (self.img_cnt >=2):
				alt_value = self.get_attr_value("alt", attrs)
				self.alt=alt_value
			self.img_cnt = self.img_cnt + 1
		
		if (tag == "a" and self.alt == "[DIR]"):
			href_value = self.get_attr_value("href", attrs)
			self.dir.append(href_value)
		elif (tag == "a" and self.alt != ""):
			href_value = self.get_attr_value("href", attrs)
			self.file.append(href_value)

#latest time.
#must be of the same length.
def time_cmp(t1, t2):
	for i in range(len(t1)):
		if (t1[i] != t2[i]):
			break
	if (i < len(t1)):
		return int(t1[i]) - int(t2[i])
	return 0

def get_latest_time_fromsite(username, password):
	url = "https://topo-data.caida.org/team-probing/list-7.allpref24/"
	passwd_mgr = urllib2.HTTPPasswordMgrWithDefaultRealm()
	passwd_mgr.add_password("topo-data", url, username, password)

	opener = urllib2.build_opener(urllib2.HTTPBasicAuthHandler(passwd_mgr))
	team_dir = ["team-1/daily/", "team-2/daily/", "team-3/daily/"]; 

	temp = []
	for t in team_dir:
		f = opener.open(url+t)
		text = f.read()
		parser = CaidaParser()
		parser.feed(text)
		
		e = parser.dir[-1].strip('/')
		temp.append(parse_latest_year(url+t+e, opener))
	
	res = temp[0]
	for t in temp[1:]:
		if(time_cmp(t, res) > 0):
			res = t
	
	return res

def parse_latest_year(url, opener):
	f = opener.open(url)
	text = f.read()
	
	parser = CaidaParser()
	parser.feed(text)
	
	res = parser.dir[-1]
	res = res.split('-')[1].strip('/')
	return res

#url list of files with specified time.
def get_time_list_fromsite(target_time, username, password):
	url = "https://topo-data.caida.org/team-probing/list-7.allpref24/"
	passwd_mgr = urllib2.HTTPPasswordMgrWithDefaultRealm()
	passwd_mgr.add_password("topo-data", url, username, password)

	opener = urllib2.build_opener(urllib2.HTTPBasicAuthHandler(passwd_mgr))
	team_dir = ["team-1/daily/", "team-2/daily/", "team-3/daily/"]; 

	res = []
	for t in team_dir:
		f = opener.open(url+t)
		text = f.read()
		parser = CaidaParser()
		parser.feed(text)
		
		target_year = target_time[:4]
	
		for e in parser.dir:
			if(time_cmp(e.strip('/'), target_year) == 0):
				temp = parse_year_dir(target_time, url+t+e, opener)
				res.extend(temp)
				break
	
	return res

def parse_year_dir(target_time, url, opener):
	f = opener.open(url)
	text = f.read()
	
	parser = CaidaParser()
	parser.feed(text)

	for e in parser.dir:
		time = e.split('-')[1].strip('/')
		if (time_cmp(time, target_time) == 0):
			res = parse_time_dir(url+e, opener)
			return res
	
	return []

def parse_time_dir(url, opener):
	f = opener.open(url)
	text = f.read()
	
	parser = CaidaParser()
	parser.feed(text)

	res = []
	for e in parser.file:
		if ( len(e.split('.')) != 8 ):
			continue
		res.append(url+e)
	
	return res

#caida restricted.
def download_caida_restricted_wrapper(argv, resource):
	url = argv[0]
	dir = argv[1]
	file= argv[2]
	username= argv[3]
	password= argv[4]
	
	proxy = resource[0]
	return download_caida_restricted_worker(url, dir, file, username, password, proxy)

def download_caida_restricted_worker(url, dir, file, username, password, proxy=""):
	passwd_mgr = urllib2.HTTPPasswordMgrWithDefaultRealm()
	passwd_mgr.add_password("topo-data", url, username, password)

	opener = urllib2.build_opener(urllib2.HTTPBasicAuthHandler(passwd_mgr))

	if(True): #ignore proxy
		opener.add_handler(urllib2.ProxyHandler({"http":proxy}))

	if not os.path.exists(dir):
		os.makedirs(dir)

	res = True
	ex = None
	try:
		if not os.path.exists(dir+file):
			print "Started downloading %s" % (dir+file)
			f = opener.open(url, timeout=10)
			fp = open(dir+file, 'wb')
			fp.write(f.read())
			fp.close()
			f.close()
		else:
			print "Skipping existing file: %s" % (dir+file)
	except Exception, e:
		print e
		res = False
		if os.path.exists(dir+file):
			os.remove(dir+file)
	
	if res:
		print url.split('/')[-1] + " " + proxy + " " + str(res) + " " + (str(ex) if ex!=None else "succeeded")
	
	return res

def download_date(date, root_dir="data/", proxy_file="", mt_num=-1):
	auth_info = load_auth("accounts.json")
	username = auth_info["username"]
	password = auth_info["password"]
	#get url list.
	is_succeeded = False
	round_cnt = 1
	while(not is_succeeded):
		try:
			url_list = get_time_list_fromsite(date, username, password)
			is_succeeded = True
		except Exception, e:
			print e
			is_succeed = False
			round_cnt = round_cnt + 1
			time.sleep(1*round_cnt)

	#destination directory.
	dir = root_dir+"/"+date+"/"
	if (not os.path.exists(dir)):
		os.makedirs(dir)
	
	#proxy_list.
	proxy_list = []
	fp = open(proxy_file,'rb')
	for line in fp.readlines():
		proxy_list.append( [line.strip('\n')] ); #note that proxy_list here act as resource_list.
	
	#build argv_list
	argv_list = []
	for url in url_list:
		team = url.split('/')[5]
		suffix = url.split('/')[-1].split('.',4)[-1]
		file = team+"."+suffix
		if( os.path.exists(dir+file) ):
			continue

		argv = (url, dir, file, username, password)
		argv_list.append(argv)
	
	#run with multi thread.
	multi_thread.run_with_multi_thread(download_caida_restricted_wrapper, argv_list, proxy_list, mt_num)
