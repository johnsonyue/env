import sys

from geoip import geoip

def printg(node,edge):
	print_num(node,edge)
	print_node(node)
	print_edge(edge)

def print_num(node, edge):
	print str(len(node)) + " " + str(len(edge.keys()))

def print_node(node):
	for n in node:
		print n
def print_edge(edge):
	for e in edge:
		print str(e[0]) + " " + str(e[1])

def main(argv):
	node = []
	node_dict = {}
	edge = {}
	tnode = []
	
	num_node=0
	num_edge=0
	geoip = geoip.geoip_helper()
	while (True):
		try:
			line=raw_input()
			if (not num_edge):
				del tnode
				tnode = []
				num_node=int(line.split(' ')[0])
				num_edge=int(line.split(' ')[1].strip('\n'))
				#sys.stderr.write("%s,%s\n"%(num_node,num_edge))
				
			elif (num_node):
				n=line.strip('\n')
				tnode.append(n)
				num_node-=1
			else:
				e=line.strip('\n')
				src=tnode[e.split(' ')[0]]
				dst=tnode[e.split(' ')[1]]
				country_src=geoip.query(src)["mmdb"]["country"]
				country_dst=geoip.query(dst)["mmdb"]["country"]
				if (country_src=="AF" or country_dst=="AF"):
					if(not node_dict.has_key(src)):
						index_src=len(node)
						node.append(src)
						node_dict[src]=index_src
					else:
						index_src=node_dict[src]

					if(not node_dict.has_key(dst)):
						index_dst=len(node)
						node.append(dst)
						node_dict[dst]=index_dst
					else:
						index_src=node_dict[dst]
					
					edge[(index_src,index_dst)]=""
						
				num_edge-=1
		except EOFError:
			break
		except Exception, e:
			sys.stderr.write("%s\n"%(e))
			break

if __name__ == "__main__":
	main(sys.argv)
