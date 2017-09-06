import sys
import getopt
from sets import Set

router_list = []
ip2router = {}
edge_dict = {}

def aggr(a,b):
	rid = ip2router[a] if ip2router.has_key(a) else (ip2router[b] if ip2router.has_key(b) else -1)
	if rid < 0:
		rid = len(router_list)
		router_list.append(Set([a,b]))
		ip2router[a] = rid
		ip2router[b] = rid
	else:
		router_list[rid].add(a)
		router_list[rid].add(b)
	return rid

'''
def merge(a,b):
	if a[0] == 'Y':
		a[0] = b[0]
	a[3] = str(int(a[3]) + int(b[3]))
	for i in [1,2,4,5]:
		if a[i] > b[i]:
			a[i] = b[i]
	return a
'''
def merge(a,b):
	if a[1] == 'I':
		a[1] = b[1]
	if a[0] > b[0]:
		a[0] = b[0]
	return a

def insert(a,b,attr):
	aid = (ip2router[a] if ip2router.has_key(a) else len(router_list))
	if ( aid == len(router_list) ):
		router_list.append(Set([a]))
		ip2router[a] = aid
	bid = (ip2router[b] if ip2router.has_key(b) else len(router_list))
	if ( bid == len(router_list) ):
		router_list.append(Set([b]))
		ip2router[b] = aid
	
	if not edge_dict.has_key((aid,bid)):
		edge_dict[(aid,bid)] = attr
	else:
		edge_dict[(aid,bid)] = merge(edge_dict[(aid,bid)],attr)

def process(alias,edge,prefix):
	#read
	with open(alias,'rb') as af:
		for line in af.readlines():
			line=line.strip('\n')
			aggr(line.split(' ')[0],line.split(' ')[1])
	af.close()

	with open(edge,'rb') as ef:
		for line in ef.readlines():
			line=line.strip('\n')
			insert(line.split(',')[0],line.split(',')[1],line.split(',')[2:])
	ef.close()
	
	#write
	with open(prefix+".node",'wb') as of:
		for i in range(len(router_list)):
			of.write( "Node" + str(i) + ":" )
			r = router_list[i]
			if_str = ""
			for f in r:
				if_str += f+" "
			of.write( if_str.strip(" ") + "\n")
	of.close()

	with open(prefix+".edge",'wb') as of:
		for k,v in edge_dict.items():
			of.write("Node" + str(k[0]) + ",Node" + str(k[1]))
			for f in v:
				of.write(" " + str(f))
			of.write("\n")
	of.close()

def usage():
	print "rtrtopo -e <$edge-file> -a <$alias-file>"

def main(argv):
	try:
		opts, args = getopt.getopt(argv[1:], "ha:e:p:")
	except getopt.GetoptError as err:
		print str(err)
		usage()
		exit(2)

	alias = ""
	edge = ""
	prefix = "default"
	for o,a in opts:
		if o == "-h":
			usage()
			exit(0)
		elif o == "-a":
			alias = a
		elif o == "-e":
			edge = a
		elif o == "-p":
			prefix = a
		
	if alias == "" or edge == "":
		usage()
		exit(2)
	
	process(alias,edge,prefix)

if __name__ == "__main__":
	main(sys.argv)
