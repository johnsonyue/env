import json
import os
import sys

from manager import manager

def main(argv):
	config = json.loads(open("config.json").read())
	state_file_name = config["manager"]["state_file_name"]
	data_dir = config["worker"]["root_dir"]
	if ( not os.path.exists("%s" % (state_file_name)) ):
		manager.update_path_state_file(state_file_name, data_dir, is_init=True)
	else:
		manager.update_path_state_file(state_file_name, data_dir, is_init=False)
	
if __name__ == "__main__":
	main(sys.argv)
