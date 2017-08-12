import HTMLParser
import urllib2
import os
import json
import math
import time
import datetime
import subprocess

import multi_thread

base_url = "https://atlas.ripe.net/api/v2/"

#categorize by one-off
#use probe as ground truth
def download_ripe_atlas_detail_worker_wrapper(argv, resource):
	url=argv[0]
	temp_list=argv[1]
	ind=argv[2]
	proxy=resource[0]
	return download_ripe_atlas_detail_worker(url, temp_list, ind, proxy)

def download_ripe_atlas_detail_worker(url, temp_list, ind, proxy=""):
	opener = urllib2.build_opener(urllib2.HTTPBasicAuthHandler())
	opener.add_handler(urllib2.ProxyHandler({"http":proxy}))

	res = True
	ex = None
	text = ""
	try:
		f = opener.open(url, timeout=10)
		text = f.read()
		f.close()
	except Exception, e:
		print e
		res = False
		if os.path.exists(dir+file):
			os.remove(dir+file)
	
	if res:
		print url.split('/')[-1] + " " + proxy + " " + str(res) + " succeeded " + str(ind)

	temp_list[ind]=text
	return res

def download_ripe_atlas_list_mt_wrapper(argv, resource):
	url=argv[0]
	temp_list=argv[1]
	ind=argv[2]
	proxy=resource[0]
	text=download_ripe_atlas_list_worker(url,proxy)
	if text == False:
		return False

	page=json.loads(text)
	temp_list[ind] = page["results"]
	return True
	
def download_ripe_atlas_list_worker(url, proxy=""):
	opener = urllib2.build_opener(urllib2.HTTPBasicAuthHandler())
	opener.add_handler(urllib2.ProxyHandler({"http":proxy}))

	res = True
	ex = None
	text = ""
	try:
		f = opener.open(url, timeout=10)
		text=f.read()
		f.close()
	except Exception, e:
		print e
		res = False
	
	if res:
		print url.split('/')[-1] + " " + proxy + " " + str(res) + " " + (str(ex) if ex!=None else "succeeded")
	else:
		return False
	
	return text

def construct_url(base, params):
	url=base+"/?"
	for k in params.keys():
		url+="%s=%s&"%(k,params[k])
	
	return url.strip("&")

def get_measurements_list(start_ts, stop_ts, mt_num):
	page_size=500
	
	measurements_url = base_url+"/measurements/"
	params={}
	params["format"]="json"
	params["page_size"]=str(page_size)
	params["is_public"]="true"
	params["type"]="traceroute"
	params["af"]="4"
	params["start_time__gte"]=start_ts
	params["stop_time_lte"]=stop_ts
	
	result_list=[]
	#first page
	url=construct_url(measurements_url, params)
	page=json.loads(download_ripe_atlas_list_worker(url,""))
	page_num=int(math.ceil(float(page["count"])/page_size))
	result_list.extend( page["results"] )
	
	temp_list=[ "" for i in range(page_num+1) ]
	#proxy_list.
	proxy_list = [[""]]
	
	#build argv_list
	argv_list = []
	for i in range(2,page_num+1):
		params["page"] = str(i)
		url = construct_url(measurements_url, params)
		ind = i
		argv = (url, temp_list, ind)
		argv_list.append(argv)
	
	#run with multi thread.
	multi_thread.run_with_multi_thread(download_ripe_atlas_list_mt_wrapper, argv_list, proxy_list, mt_num)

	for i in range(2, page_num+1):
		result_list.extend( temp_list[i] )

	return result_list

def download_date(date, root_dir="data/", proxy_file="", mt_num=-1):
	start_ts=int(time.mktime(datetime.datetime.strptime(date, "%Y%m%d").timetuple()))
	stop_ts=start_ts+24*60*60+1

	#get url list.
	is_succeeded = False
	round_cnt = 1
	while(not is_succeeded):
		try:
			result_list = get_measurements_list(start_ts, stop_ts, mt_num)
			is_succeeded = True
		except Exception, e:
			print e
			is_succeed = False
			round_cnt = round_cnt + 1
			time.sleep(1*round_cnt)
	
	url_list=[]
	for r in result_list:
		url_list.append(r["result"])
	
	#temp_list to contain result content of result_list
	temp_list=[ "" for i in range(len(url_list)) ]

	#destination directory.
	dir = root_dir+"/"+date+"/"
	if (not os.path.exists(dir)):
		os.makedirs(dir)
	
	#proxy_list.
	proxy_list = []
	fp = open(proxy_file,'rb')
	for line in fp.readlines():
		proxy_list.append( [line.strip('\n')] ); #note that proxy_list here act as resource_list.
	fp.close()
	
	#build argv_list
	argv_list = []
	for i in range(len(url_list)):
		url=url_list[i]
		ind=i
		argv = (url, temp_list, ind)
		argv_list.append(argv)
	
	#run with multi thread.
	multi_thread.run_with_multi_thread(download_ripe_atlas_detail_worker_wrapper, argv_list, proxy_list, mt_num)
	
	print "writting to file ... "
	for i in range(len(result_list)):
		result_list[i]["results_json"]=temp_list[i]
	file=date+".ripe"
	fp = open(dir+"/"+file+".ripe.tar.gz", 'wb')
	h = subprocess.Popen(['gzip', '-c', '-'], stdin=subprocess.PIPE, stdout=fp)
	h.stdin.write(json.dumps(result_list,indent=1))
	fp.close()
