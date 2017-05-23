import urllib2
import json
import os
import re
import sys
import math
import HTMLParser

import multi_thread

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

#load authentication info.
def load_auth(auth_file):
	j = json.loads( open(auth_file,'r').read() )
	return { "username":j["caida"]["username"], "password":j["caida"]["password"] }

def get_page_files(url, username, password):
	passwd_mgr = urllib2.HTTPPasswordMgrWithDefaultRealm()
	passwd_mgr.add_password("topo-data", url, username, password)

	opener = urllib2.build_opener(urllib2.HTTPBasicAuthHandler(passwd_mgr))

	f = opener.open(url)
	text = f.read()
	parser = CaidaParser()
	parser.feed(text)
	
	return parser.file

def get_caida_file_size(opener, url):
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

def download_caida_restricted_wrapper(argv, resource):
	url=argv[0]
	opener=argv[1]
	dst_dir=argv[2]
	file_name=argv[3]
	start=argv[4]
	end=argv[5]
	
	proxy=resource[0]
	return download_segemented_caida_restricted_worker(url, opener, dst_dir, file_name, start, end, proxy)

def download_segemented_caida_restricted_worker(url, opener, dst_dir, file_name, start, end, proxy=""):
	request=urllib2.Request(url)
	request.add_header( "Range", "bytes="+str(start)+"-"+str(end) )
	request.add_header("User-agent", "Mozila/5.0")

	print ("downloading "+file_name+" "+str(start/1024)+"K"+"-"+str(end/1024)+"K"+" with proxy "+proxy+" start:"+str(start)+" end:"+str(end))
	sys.stdout.flush()
	if(proxy != ""):
		opener.add_handler(urllib2.ProxyHandler({"http":proxy}))

	if not os.path.exists(dst_dir):
		os.makedst_dirs(dst_dir)

	res = True
	ex = None
	try:
		if not os.path.exists(dst_dir+"/"+file_name):
			f = opener.open(request, timeout=10)
			fp = open(dst_dir+"/"+file_name, 'wb')
			#print f.info()
			#print f.code
			fp.write(f.read())
			fp.close()
			f.close()
	except Exception, e:
		print e
		ex = e
		res = False
		if os.path.exists(dst_dir+"/"+file_name):
			os.remove(dst_dir+"/"+file_name)
	
	if res:
		print file_name + " " + proxy + " " + str(res) + " " + (str(ex) if ex!=None else "succeeded")
		sys.stdout.flush()
	
	return res

def assemble_segements(dst_dir, file_name):
	print "assembling segements ... "
	if not os.path.exists(dst_dir):
		os.makedirs(dst_dir)

	file_list = os.listdir(dst_dir)
	num_file = 0
	for fn in file_list:
		if(re.findall(file_name+".\d+", fn)):
			num_file = num_file + 1
	
	fp = open(dst_dir+"/"+file_name, 'wb')
	for i in range(num_file):
		fn = dst_dir+"/"+file_name+"."+str(i)
		f = open(fn, 'rb')
		fp.write(f.read())
		f.close()
		os.system("rm -f "+fn)
	
	fp.close()
	print "finished assembling segements"
	
	return ""

def download_file(url, dst_dir, file_name, username, password, proxy_list, seg_size=20*1024*1024, mt_num=-1):
	#build opener for each file to be downloaded
	passwd_mgr = urllib2.HTTPPasswordMgrWithDefaultRealm()
	passwd_mgr.add_password("topo-data", url, username, password)

	opener = urllib2.build_opener(urllib2.HTTPBasicAuthHandler(passwd_mgr))

	#get the size first.
	file_size = get_caida_file_size(opener, url)
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
	
	#build argv_list.
	argv_list=[]
	for i in range(len(range_list)):
		r=range_list[i]
		fn="%s.%s" % (file_name,i)
		argv=(url,opener,dst_dir,fn,r[0],r[1])
		argv_list.append(argv)
	
	#run with multi thread.
	multi_thread.run_with_multi_thread(download_caida_restricted_wrapper, argv_list, proxy_list, mt_num)
	
	#assemble segements.
	assemble_segements(dst_dir, file_name)

def download_page(url, dst_dir, username, password, proxy_file):
	if ( not os.path.exists(dst_dir) ):
		os.makedirs(dst_dir)
	#proxy_list
	proxy_list = []
	fp = open(proxy_file,'rb')
	for line in fp.readlines():
		proxy_list.append( [line.strip('\n')] )
	fp.close()

	file_list=get_page_files(url, username, password)
	for f in file_list:
		download_file(url+"/"+f, dst_dir, f, username, password, proxy_list, mt_num=3)

def main():
	url = "https://topo-data.caida.org/ITDK/ITDK-2016-09/"
	auth=load_auth("accounts.json")
	username=auth["username"]
	password=auth["password"]

	download_page(url, "itdk/", username, password, "proxy_list")
	
if __name__ == "__main__":
	main()
