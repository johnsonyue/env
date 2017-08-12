import json
import os
import sys

from worker import caida
from manager import manager

def usage():
	print "python cron.py <source>"

def main(argv):
	if (len(argv) < 2):
		usage()
		exit()
	source = argv[1]

	start_time = "20070913"
	config = json.loads( open("config.json",'r').read() )
	state_file_name = config["manager"]["state_file_name"]

	if (source == "caida"):
		print "getting latest time ... "
		auth_info = caida.load_auth("accounts.json") #relative to pwd
		username = auth_info["username"]
		password = auth_info["password"]
		date = caida.get_latest_time_fromsite(username, password)
		#date="20170303"
		if ( not os.path.exists("%s" % (state_file_name)) ):
			manager.update_state_file("%s" % (state_file_name), date, start_time="20070913",is_init=True);
		else:
			manager.update_state_file("%s" % (state_file_name), date, start_time="20070913");

if __name__ == "__main__":
	main(sys.argv)
