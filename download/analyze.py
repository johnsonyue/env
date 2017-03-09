import time
import json
import os
import sys

from worker import request_handler

def usage():
	print "python analyze.py <source>"

def main(argv):
	if len(argv) < 2:
		usage()
		exit()
	
	data_source = argv[1]
	handler = request_handler.RequestHandler("config.json")
	
	config = json.loads(open("config.json").read())

	if data_source == "caida":
		root_dir = config["worker"]["root_dir"]
		out_dir = config["worker"]["out_dir"]
		if (not os.path.exists(out_dir)):
			os.makedirs(out_dir)
		date = ""
		try:
			while(True):
				date = handler.get_task(data_source)
				print date
				sys.stdout.flush()
				
				start_time = time.time()
				print handler.notify_started(date,data_source),
				sys.stdout.flush()
				
				print "../analyze/decode.sh %s %s %s | python ../analyze/uniform.py %s | python ../analyze/analyze.py >%s/%s.graph" % (data_source, root_dir, date, data_source, out_dir, date)
				os.chdir( "../analyze" )
				os.system( "decode.sh %s %s %s | python uniform.py %s | python analyze.py >%s/%s.graph" % (data_source, root_dir, date, data_source, out_dir, date) )
				os.chdir( "../download" )
				time.sleep(5)
		
				end_time = time.time()
				time_used = end_time - start_time
				print handler.notify_finished(date, time_used, data_source),
				sys.stdout.flush()
		except Exception, e:
			print e
			print handler.notify_terminated(date,data_source)
			pass

if __name__ == "__main__":
	main(sys.argv)
