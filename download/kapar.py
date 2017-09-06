import sys

from worker import caida

def main(argv):
	auth_info=caida.load_auth("accounts.json")
	username=auth_info["username"]
	password=auth_info["password"]
	url="https://topo-data.caida.org/ITDK/ITDK-2017-02/kapar-midar-iff.ifaces.bz2"
	dir="."
	file="kapar-midar-iff.ifaces.bz2"
	caida.download_caida_restricted_worker(url, dir, file, username, password, proxy="")

if __name__ == "__main__":
	main(sys.argv)
