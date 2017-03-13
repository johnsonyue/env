import HTMLParser
import urllib
import urllib2
import sys
import os
import cookielib
import time
import math
import json

import multi_thread

#html parsers.
class iPlaneParser(HTMLParser.HTMLParser):
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

#load authentication info.
def load_auth(auth_file):
	j = json.loads( open(auth_file,'r').read() )
	return { "username":j["iplane"]["username"], "password":j["iplane"]["password"] }

def get_iplane_opener(username, password):
	print "logging in..."
	login_url = "https://access.ripe.net/?originalUrl=https%3A%2F%2Fdata-store.ripe.net%2Fdatasets%2Fiplane-traceroutes%2F&service=datarepo"
	params = { "username": username, "password": password }; 
	cj = cookielib.CookieJar()
	opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
	post_data = urllib.urlencode(params).encode('utf-8')

	f = opener.open(login_url, post_data)
	print "done."

	return opener

def get_iplane_file_size(opener, url):
	request=urllib2.Request(url)
	request.add_header("Range", "bytes=0-10737418240")
	try:
		f = opener.open(request)
		res = int(f.info()["Content-Length"])
		f.close()
		print res, str(res/1024/1024)+" MB"
	except:
		print "remote file not found: "+url
		return -1

	return res

def get_latest_time_fromsite(username, password, reversed=False):
	url = "https://data-store.ripe.net/datasets/iplane-traceroutes/"
		
	opener = get_iplane_opener(username, password)

	f = opener.open(url)
	text = f.read()

	parser = iPlaneParser()
	parser.feed(text)
	
	if (not reversed):
		e = parser.dir[-1].strip('/')
	else:
		e = parser.dir[0].strip('/')
	res = parse_latest_year(url+e, opener, reversed)
	
	return res

def parse_latest_year(url, opener, reversed):
	f = opener.open(url)
	text = f.read()
	
	parser = iPlaneParser()
	parser.feed(text)
	
	if (not reversed):
		result = parser.file[-1]
	else:
		result = parser.file[0]
	lst = result.split('.')[0].split('_')
	result = lst[1]+lst[2]+lst[3]
	
	return result
	
def construct_url_fromtime(target_time):
	url = "https://data-store.ripe.net/datasets/iplane-traceroutes/"
	target_year = target_time[:4]
	target_month = target_time[4:6]
	target_day = target_time[6:8]
	
	res = url+target_year+"/traces_"+target_year+"_"+target_month+"_"+target_day+".tar.gz"

	return res

#downloading with multi-thread support.
def download_iplane_restricted_wrapper(argv, resource):
	url = argv[0]
	dir = argv[1]
	file= argv[2]
	opener = argv[3]
	start = argv[4]
	end = argv[5]
	
	proxy = resource[0]
	return download_segemented_iplane_restricted_worker(url,dir,file,opener,start,end,proxy)

def download_segemented_iplane_restricted_worker(url, dir, file, opener, start, end, proxy=""):
	request=urllib2.Request(url)
	request.add_header( "Range", "bytes="+str(start)+"-"+str(end) )
	request.add_header("User-agent", "Mozila/5.0")

	print ("downloading "+file+" "+str(start/1024)+"K"+"-"+str(end/1024)+"K"+" with proxy "+proxy+" start:"+str(start)+" end:"+str(end))
	sys.stdout.flush()
	if(proxy != ""):
		opener.add_handler(urllib2.ProxyHandler({"http":proxy}))

	if not os.path.exists(dir):
		os.makedirs(dir)

	res = True
	ex = None
	try:
		if not os.path.exists(dir+file):
			f = opener.open(request, timeout=10)
			fp = open(dir+file, 'wb')
			#print f.info()
			#print f.code
			fp.write(f.read())
			fp.close()
			f.close()
	except Exception, e:
		print e
		ex = e
		res = False
		if os.path.exists(dir+file):
			os.remove(dir+file)
	
	if res:
		print file + " " + proxy + " " + str(res) + " " + (str(ex) if ex!=None else "succeeded")
		sys.stdout.flush()

def assemble_segements(dir, file):
	print "assembling segements ... "
	if not os.path.exists(dir):
		os.makedirs(dir)

	file_list = os.listdir(dir)
	num_file = 0
	for fn in file_list:
		if(re.findall(file+".\d+", fn)):
			num_file = num_file + 1
	
	fp = open(dir+"/"+file, 'wb')
	for i in range(num_file):
		fn = dir+"/"+file+"."+str(i)
		f = open(fn, 'rb')
		fp.write(f.read())
		f.close()
		os.system("rm -f "+fn)
	
	fp.close()
	print "finished assembling segements"
	
	return ""

def download_date(date, root_dir="data/", proxy_file="", seg_size=20*1024*1024, mt_num=0):
	auth_info = load_auth("accounts.json")
	is_succeeded = False
	url = construct_url_fromtime(date)

	dir = root_dir+"/"+date+"/"
	file = url.split('/')[-1]
	if (not os.path.exists(dir)):
		os.makedirs(dir)
	
	opener = get_iplane_opener(auth_info["username"], auth_info["password"])

	#get the size first.
	file_size = get_iplane_file_size(opener, url)
	if file_size == -1:
		return
	print "file_size: "+str(file_size)
	file_num = int(math.ceil(float(file_size)/seg_size))
	if file_num == 0:
		return
	
	#to get the range list.
	range_list = []
	for i in range(0,file_num-1):
		range_list.append((i*seg_size, (i+1)*seg_size-1))
	if (file_num == 1):
		i = -1
	range_list.append(((i+1)*seg_size, file_size))
	
	#proxy_list
	proxy_list = []
	fp = open(proxy_file,'rb')
	for line in fp.readlines():
		proxy_list.append(line.strip('\n'))
	fp.close()
	
	#build argv_list.
	argv_list=[]
	for i in range(len(range_list)):
		r=range_list[i]
		fn="%s.%s" % (file,i)
		argv=(url,dir,fn,opener,r[0],r[1])
		argv_list.append(argv)
	
	#run with multi thread.
	multi_thread.run_with_multi_thread(download_iplane_restricted_wrapper, argv_list, proxy_list, mt_num)
	
	#assemble segements.
	assemble_segements(dir, file)
