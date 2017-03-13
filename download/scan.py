import json
import os
import sys

from manager import manager

def usage():
	print "python scan.py <source>"

def main(argv):
	if (len(argv) <2):
		usage()
		exit()

	source = argv[0]
	config = json.loads(open("config.json").read())
	state_file_name = config["manager"]["state_file_name"]
	data_dir = config["worker"]["root_dir"]
	if ( not os.path.exists("%s" % (state_file_name)) ):
		manager.update_path_state_file(state_file_name, data_dir, is_init=True)
	else:
		manager.update_path_state_file(state_file_name, data_dir, is_init=False)
	
if __name__ == "__main__":
	main(sys.argv)
