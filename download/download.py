import sys
import time
import json

from worker import caida, request_handler

def usage():
	print "python download.py <source>"

def main(argv):
	if len(argv) < 2:
		usage()
		exit()
	
	data_source = argv[1]
	handler = request_handler.RequestHandler("config.json")
	
	config = json.loads(open("config.json").read())

	if data_source == "caida":
		proxy_file = config["worker"]["proxy_file"]
		root_dir = config["worker"]["root_dir"]
		date = ""
		while(True):
			try:
				date = handler.get_task(data_source)
				print date
				sys.stdout.flush()
				
				start_time = time.time()
				print handler.notify_started(date,data_source),
				sys.stdout.flush()
		
				caida.download_date(date, root_dir=root_dir, proxy_file=proxy_file, mt_num=4)
		
				end_time = time.time()
				time_used = end_time - start_time
				print handler.notify_finished(date, time_used, data_source),
				sys.stdout.flush()
			except KeyboardInterrupt:
				print "ctrl-c"
				print handler.notify_terminated(date,data_source)
				break
			except Exception, e:
				print e
				break

if __name__ == "__main__":
	main(sys.argv)
