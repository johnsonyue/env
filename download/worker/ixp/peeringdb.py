import urllib
import json
import datetime
import os
import sys

import multi_thread

def read_id_wrapper(argv, resource):
	url = argv[0]
	i = argv[1]
	list_obj = argv[2]

	h = urllib.urlopen(url)
	try:
		read_obj = json.loads(h.read())
	except:
		h.close()
		print url + "false"
		return False

	h.close()
	list_obj["data"][i]["read"] = read_obj
	print url + "true"
	return True

def recursive_read(url):
	h = urllib.urlopen(url)
	list_obj = json.loads(h.read())
	h.close()

	url_list = []
	for item in list_obj["data"]:
		url_list.append(url+"/"+str(item["id"]))

	#build argv_list
	argv_list = []
	for i in range(len(url_list)):
		url = url_list[i]
		argv = (url,i,list_obj)
		argv_list.append(argv)
	
	#run with multi thread.
	multi_thread.run_with_multi_thread(read_id_wrapper, argv_list, [""], 20)

	return list_obj
		
def update_peeringdb(dst_dir):
	seed_url = "https://www.peeringdb.com/api/"
	
	temp_dir = "peeringdb_tmp"
	prefix=dst_dir+"/"+temp_dir
	if not os.path.exists(prefix):
		os.makedirs(prefix)

	sys.stderr.write(" ... downloading peeringdb_seed ... ")
	sys.stderr.flush()
	urllib.urlretrieve(seed_url, prefix+"/peeringdb_seed")
	sys.stderr.write("done.\n")
	
	seed_json=json.loads(open(prefix+"/peeringdb_seed",'rb').read())
	file_list=[]
	url_list=[]
	for k,v in seed_json.items():
		if k[0] == "_":
			continue
		file_list.append("peeringdb_"+k)
		url_list.append(seed_url+v["list"]["url"])
	
	for i in range(len(file_list)):
		f=file_list[i]
		url=url_list[i]
		sys.stderr.write(" ... downloading %s ... " % (f))
		sys.stderr.flush()
		
		with open(prefix+"/"+f,'wb') as fp:
			json.dump(recursive_read(url),fp)
		sys.stderr.write("done.\n")
	
	db_json=json.loads(open(prefix+"/"+file_list[0]).read())
	timestamp=int(db_json["meta"]["generated"])
	date=datetime.datetime.fromtimestamp(timestamp).strftime("%Y%m%d.%H00")
	
	os.system("mv %s %s" % (dst_dir+"/"+temp_dir, dst_dir+"/peeringdb-"+date))
	return dst_dir+"/peeringdb-"+date
