import sys

from geoip import geoip

def merge_into(tnode,tedge,node_dict,node,edge):
	for e in tedge:
		src=tnode[e[0]]
		if (not node_dict.has_key(src)):
			src_index=len(node)
			node.append(src)
			node_dict[src]=src_index
		else:
			src_index=node_dict[src]
		dst=tnode[e[1]]
		if (not node_dict.has_key(dst)):
			dst_index=len(node)
			node.append(dst)
			node_dict[dst]=dst_index
		else:
			dst_index=node_dict[dst]
		edge[(src_index,dst_index)]=""

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
	tedge = {}
	
	num_node=0
	num_edge=0
	geoip = geoip.geoip_helper()
	while (True):
		try:
			line=raw_input()
			if (line.strip('\n') == "###"):
				#sys.stderr.write("merge\n")
				merge_into(tnode,tedge,node_dict,node,edge)
				del tnode
				del tedge
				tnode = []
				tedge = {}
				continue
			if (not num_edge):
				num_node=int(line.split(' ')[0])
				num_edge=int(line.split(' ')[1].strip('\n'))
				#sys.stderr.write("%s,%s\n"%(num_node,num_edge))
				
			elif (num_node):
				n=line.strip('\n')
				geo = geoip.query(n)
				if (geo["mmdb"]["country"] == "AF"):
					tnode.append(n)
				num_node-=1
			else:
				e=line.strip('\n')
				tedge[(int((e.split(' ')[0])), int(e.split(' ')[1]))]=""
				num_edge-=1
		except EOFError:
			break
		except Exception, e:
			sys.stderr.write("%s\n"%(e))
			break

if __name__ == "__main__":
	main(sys.argv)
