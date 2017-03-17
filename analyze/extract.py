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
	tnode_dict = {}
	
	num_node=0
	num_edge=0
	geo = geoip.geoip_helper()
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
				country=geo.query(n)["mmdb"]["country"]
				if (country=="AF"):
					tnode_dict[n]=""
				num_node-=1
			else:
				print_node(node)
				break
				e=line.strip('\n')
				src=int(e.split(' ')[0])
				dst=int(e.split(' ')[1])
				if (tnode_dict.has_key(src) or tnode_dict.has_key(dst)):
					src_ip=tnode[src]
					dst_ip=tnode[dst]
					if(not node_dict.has_key(src_ip)):
						index_src=len(node)
						node.append(src_ip)
						node_dict[src_ip]=index_src
					else:
						index_src=node_dict[src_ip]

					if(not node_dict.has_key(dst_ip)):
						index_dst=len(node)
						node.append(dst_ip)
						node_dict[dst_ip]=index_dst
					else:
						index_src=node_dict[dst_ip]
					
					edge[(index_src,index_dst)]=""
						
				num_edge-=1
		except EOFError:
			printg(node, edge)
			break
		except Exception, e:
			sys.stderr.write("%s\n"%(e))
			break

if __name__ == "__main__":
	main(sys.argv)
