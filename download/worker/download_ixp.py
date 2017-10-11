import sys
import os

from ixp import bgplgdb
from ixp import wikiixp
from ixp import pch
from ixp import peeringdb

def download(dst_dir):
	tmp_path = dst_dir + "/tmp"
	if not os.path.exists(tmp_path):
		os.makedirs(tmp_path)
	
	print "bgp = bgplgdb.parse_ixp_offline()"
	bgp = bgplgdb.parse_ixp_offline()
	fp = open(dst_dir + "/" + "bgplgdb",'wb')
	for line in bgp:
		fp.write(line+"\n")
	fp.close()

	print "wiki = wikiixp.parse_ixp_wrapper()"
	wiki = wikiixp.parse_ixp_wrapper()
	fp = open(dst_dir + "/" + "wikiixp",'wb')
	for line in wiki:
		fp.write(line+"\n")
	fp.close()

	print "pch.download_pch_wrapper(dst_dir)"
	pch.download_pch_wrapper(dst_dir)

	print "peeringdb.update_peeringdb(dst_dir)"
	datetime = peeringdb.update_peeringdb(dst_dir)
	
	datetime = datetime.split('-')[-1]
	dst_path = dst_dir + "/" + datetime
	print "dst_path: " + dst_path

def main(argv):
	if len(argv) < 2:
		exit()
	dst_dir = argv[1]
	
	download(dst_dir)

if __name__ == "__main__":
	main(sys.argv)
