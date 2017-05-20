import sys
import math
import random

def is_ip_ligit(ip):
	decs=ip.split('.')
	if (len(decs)!=4):
		return False #4 decimals.
	for d in decs:
		if(d==""):
			return False
		if(int(d)>255 or int(d)<0): #not in [0-255]
			return False
		if(int(d)!=0 and d[0]=='0'): #has extra 0 pad
			return False
	return True

def ip2int(ip):
	if not is_ip_ligit(ip):
		return -1
	r=3
	i=0
	for o in ip.split('.'):
		o=int(o)
		i+=o*pow(256,r)
		r-=1
	
	return i

def is_int_ligit(i):
	if i>math.pow(2,32)-1 or i<0:
		return False
	else:
		return True

def int2ip(i):
	if not is_int_ligit(i):
		return ""
	l=[]
	q=i
	for j in range(4):
		l.append(q%256)
		q=q/256
	ip=""
	for j in range(3,-1,-1):
		ip+=str(l[j])+"."
	return ip.strip(".")

def randip():
	randip_int=random.randint(0,math.pow(2,32)-1)
	return int2ip(randip_int)

class Node():
	def __init__(self, ip):
		self.ip = ip
		self.adj_list = {}
		self.is_anonymouse = False
		self.is_reply = True
class Edge():
	def __init__(self, ind_in, ind_out, delay):
		self.ind_in = ind_in
		self.ind_out = ind_out
		self.delay = delay

class Graph():
	def __init__(self):
		self.max_delay = 100
		self.nodes = [] #adjacent list
		self.edges = [] #edge list
		self.edge_dict = {}
		self.node_dict = {} #dictionaries for quick look up.
	
	def add_node(self, node):
		#print "Add node: %s" % (node.ip), #debug
		if (not self.node_dict.has_key(node)):
			index=len(self.nodes)
			self.node_dict[node]=index
			self.nodes.append(node)
		#print " %s" % (index) #debug
		return index
	
	def add_edge(self, edge):
		#print "Add edge: %s, %s" % (edge.ind_in, edge.ind_out) #debug
		if ( not self.edge_dict.has_key((edge.ind_in, edge.ind_out)) ):
			index=len(self.edges)
			self.edges.append(edge)
			self.edge_dict[(edge.ind_in, edge.ind_out)] = index
			ind_in = edge.ind_in
			ind_out = edge.ind_out
			self.nodes[ind_in].adj_list[ind_out]=""
			self.nodes[ind_out].adj_list[ind_in]="" #add to adjacent list.
	
	def get_degree(self, ind):
		return len(self.nodes[ind].adj_list)
	
	def rand_pick(self, num_pick):
		deg_cd=[] #cumulative distribution.
		deg_sum=0
		for i in range(len(self.nodes)):
			deg_cd.append(deg_sum)
			deg_sum+=self.get_degree(i)
		deg_cd.append(deg_sum)
		
		#print deg_cd #debug
		pick_list=[]
		i=0
		while i<num_pick:
			rand=random.randint(deg_cd[0], deg_cd[-1])
			for j in range(len(deg_cd)-1):
				if (rand>=deg_cd[j] and rand<deg_cd[j+1]):
					break
			if j in pick_list:
				continue
			pick_list.append(j)
			i+=1

		return pick_list

def generate_full_mesh(num_node):
	graph = Graph()
	for i in range(num_node):
		node=Node(randip())
		index=graph.add_node(node)
		for j in range(index):
			
			graph.add_edge(Edge(j,index,random.randint(1,graph.max_delay)))
			graph.add_edge(Edge(index,j,random.randint(1,graph.max_delay)))
	return graph

def generate_scale_free_graph(num_node):
	num_full = 4
	num_pick = 1
	graph = generate_full_mesh(num_full)
	#print "Full mesh generated" #debug
	for i in range(num_node-num_full):
		node=Node(randip())
		index=graph.add_node(node)
		pick_list=graph.rand_pick(num_pick)
		#print "%s randpick: %s" % (i, pick_list) #debug
		for p in pick_list:
			graph.add_edge(Edge(i,p,random.randint(1,graph.max_delay)))
			graph.add_edge(Edge(p,i,random.randint(1,graph.max_delay)))
	
	return graph

def dijkstra(graph, src):
	prev = [ None for i in range(len(graph.nodes)) ]
	dist = [ graph.max_delay*(len(graph.nodes)+1) for i in range(len(graph.nodes)) ]
	visited = [ False for i in range(len(graph.nodes)) ]

	dist[src] = 0
	while True:
		is_all_visited = True
		min_dist = graph.max_delay*(len(graph.nodes)+1)+1
		min_ind = None
		for i in range(len(visited)):
			if not visited[i]:
				if dist[i] < min_dist:
					min_dist = dist[i]
					min_ind = i
				is_all_visited = False
		if is_all_visited:
			return prev

		#print "min_ind %s" % (min_ind) #debug
		visited[min_ind]=True
		for adj in graph.nodes[min_ind].adj_list:
			edge_ind=graph.edge_dict[(min_ind, adj)]
			alt = graph.edges[edge_ind].delay+dist[min_ind]
			#print "adj: %s, alt: %s, dist: %s" % (adj, alt, dist[adj]) #debug
			if alt < dist[adj]:
				dist[adj] = alt
				prev[adj] = min_ind
				#print "update %s" % (adj)

def get_path(src, dst, prev):
	path=[dst]
	while dst!=src:
		dst=prev[dst]
		path.append(dst)
	return path[::-1]

def print_warts(graph, path, path_graph):
	src=path[0]
	dst=path[-1]
	prob_reply=0.5
	replied='R' if random.random()<=prob_reply else 'N'
	dst_rtt=0
	rtt_list=[]
	for i in range(len(path)-1):
		edge_ind=graph.edge_dict[(path[i],path[i+1])]
		dst_rtt+=graph.edges[edge_ind].delay
		rtt_list.append(dst_rtt)
	if replied == 'N':
		dst_rtt = 0

	prob_star=0.1
	hop_list=[]
	is_no_star=True
	for i in range(1,len(path)-1):
		p=path[i]
		hop="%s,%s,%s" % (graph.nodes[p].ip,rtt_list[i-1],1) 
		if random.random()<=prob_star:
			hop="q"
			is_no_star=False
		hop_list.append(hop)
	complete='C' if is_no_star else 'I'
	print "T\t%s\t%s\t00000000\t00000000\t00000000\t%s\t%s\t0\t0\tS\t0\t%s" \
	% ( src, dst, replied, dst_rtt, complete ),
	for h in hop_list:
		print "\t%s" % (h),
	print
	
	return

def generate_paths(graph, num_path, num_per_src):
	host_list = []
	for i in range(len(graph.nodes)):
		if graph.get_degree(i) == 1:
			host_list.append(i)
	
	path_graph=Graph()
	i=0
	while i<=num_path:
		if i%num_per_src == 0:
			src=random.randint(0,len(host_list)-1)
			prev=dijkstra(graph,src)
			dst_list=[src]
		while True:
			dst=random.randint(0,len(host_list)-1)
			if dst in dst_list:
				continue
			dst_list.append(dst)
			break

		#print get_path(src,dst,prev) #debug
		path=get_path(src,dst,prev)
		print_warts(graph,path,path_graph)
		i+=1

def main(argv):
	sf_graph=generate_scale_free_graph(3000)
	generate_paths(sf_graph,1000,10)

if __name__ == "__main__":
	main(sys.argv)
