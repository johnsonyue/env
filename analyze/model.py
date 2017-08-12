class Node():
	def __init__(self, ip):
		self.ip = ip
		self.is_router = True
		self.is_blank = False
class Edge():
	def __init__(self, ind_in, ind_out, delay):
		self.ind_in = ind_in
		self.ind_out = ind_out
		self.delay = delay
		self.is_direct = True

#node is indexed by ip
#edge is index by tuple: (ingress_index, outgress_index)
class Graph():
	def __init__(self):
		self.nodes = [] #adjacent list
		self.edges = [] #edge list
		self.edge_dict = {}
		self.node_dict = {} #dictionaries for quick look up.
	
	def add_node(self, node):
		if (not self.node_dict.has_key(node.ip)):
			index=len(self.nodes)
			self.node_dict[node.ip]=index
			self.nodes.append(node)
			return index
		else:
			return self.node_dict[node.ip]
	
	def add_edge(self, edge):
		if ( not self.edge_dict.has_key((edge.ind_in, edge.ind_out)) ):
			index=len(self.edges)
			self.edges.append(edge)
			self.edge_dict[(edge.ind_in, edge.ind_out)] = index
			ind_in = edge.ind_in
			ind_out = edge.ind_out
			return index
		else:
			return self.edge_dict[(edge.ind_in, edge.ind_out)]
