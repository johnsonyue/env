import sys
import os
import time
import math
import subprocess

import trace
import utils
import model

def insert_edge(edge,src,dst,delay):
	if ( type(src)==type((1,1,1)) ):
		return
	elif ( type(dst)==type((1,1,1)) ):
		dst=dst[2]
		if(not edge.has_key((src,dst))):
			edge[(src,dst)]=["I",delay]
		elif(edge[(src,dst)][0]=="D"):
			edge[(src,dst)][0]="B"
	else:
		if(not edge.has_key((src,dst))):
			edge[(src,dst)]=["D",delay]
		elif(edge[(src,dst)][0]=="I"):
			edge[(src,dst)][0]="B"

def get_edge_index(e,nodes):
	in_ip = nodes[e.ind_in].ip
	out_ip = nodes[e.ind_out].ip
	return (in_ip, out_ip)

def get_star_ip(n,nodes):
	in_ip=nodes[n.ip[0]].ip
	num_star=n.ip[1]
	out_ip=nodes[n.ip[2]].ip
		
	return "(%s,%s,%s)" % (in_ip, num_star, out_ip)

def store(header, graph, data_dir):
	team=header.team
	date=header.date
	true_date=header.true_date
	monitor=header.monitor
	
	nodes=graph.nodes
	edges=graph.edges

	#write to files.
	path="%s/%s"%(data_dir,date)
	if ( not os.path.exists(path) ):
		os.makedirs(path)
	
	fn="%s/%s.%s.%s.herpes_node.gz" % (path,team,true_date,monitor)
	fn2="%s/%s.%s.%s.herpes_link.gz" % (path,team,true_date,monitor)
	fp=open(fn,'w')
	fp2=open(fn2,'w')
	h = subprocess.Popen(['gzip', '-c', '-'], stdin=subprocess.PIPE, stdout=fp)
	h2 = subprocess.Popen(['gzip', '-c', '-'], stdin=subprocess.PIPE, stdout=fp2)
	
        for n in sorted( nodes, key=lambda node:node.ip ):
		if type(n.ip)==type((1,2,3)):
			star_ip=get_star_ip(n,nodes)
			h.stdin.write( "%s, R\n" % ( star_ip ) )
		else:
			is_router='R' if n.is_router else 'H'
			h.stdin.write( "%s, %s\n" % ( str(n.ip), is_router ) )
        for e in sorted( edges, key=lambda e:get_edge_index(e,nodes) ):
		in_ip = nodes[e.ind_in].ip
		out_ip = nodes[e.ind_out].ip
		is_direct = 'D' if e.is_direct else 'I'
		h2.stdin.write( "%s %s %s %s\n" % (str(in_ip), str(out_ip), is_direct, e.delay) )

	#clean up.
	h.stdin.close()
	h2.stdin.close()

def parse_hop(hop_str):
	reply_list = hop_str.split(trace.reply_delimiter)
	first_reply = reply_list[0]
	if first_reply==trace.blank_holder:
		return {}
	ip = first_reply.split(trace.ip_delimiter)[trace.hop_index["ip"]]
	rtt = float(first_reply.split(trace.ip_delimiter)[trace.hop_index["rtt"]])
	
	return {"ip":ip, "rtt":rtt}

def parse_line(line):
	field_list = line.split(trace.field_delimiter)
	dst_ip = field_list[ trace.trace_index["dst_ip"] ]
	#timestamp = field_list[ trace.trace_index["timestamp"] ]
	hops = field_list[ trace.trace_index["hops"] ]

	return {"dst_ip":dst_ip, "hops":hops}

class Header():
	def __init__(self):
		self.team=""
		self.date=""
		self.true_date=""
		self.monitor=""
	def update_from_header_line(self, line):
		fields_list=line.split(trace.header_delimiter)[1:]
		self.team=fields_list[trace.header_index["team"]]
		self.true_date=fields_list[trace.header_index["true_date"]]
		self.date=fields_list[trace.header_index["date"]]
		self.monitor=fields_list[trace.header_index["monitor"]]
	def is_empty(self):
		if (self.team and self.date and self.true_date and self.monitor):
			return False
		return True

def build_graph(data_dir):
	graph=model.Graph()
        tm = time.time()
	
	#initialize header fields.
	header=Header()
	while True:
		try:
			line = raw_input()
		except EOFError:
			store(header, graph, data_dir)
			break
		
		#handle header
		if ( line.split(trace.header_delimiter)[0] == trace.header_indicator ):
			#log progress
			t = time.time()
			sys.stderr.write( "%s,%s,%s\n" % (line, t, t-tm) )
			tm = t
			#output
			if (not header.is_empty):
				store(header, graph, data_dir)
				graph=model.Graph()
			#update header fields
			header.update_from_header_line(line)
			continue

		#handle warts line
		line_dict=parse_line(line)
		dst_ip=line_dict["dst_ip"]
		hops=line_dict["hops"]
		#print hops #debug

		#handle traceroute hops.
		hop_list = hops.split(trace.hop_delimiter)
		#print hop_list #debug
		i=0
		while (i<=len(hop_list)-1): #ignore preceding blanks.
			hop_dict=parse_hop(hop_list[i])
			if (hop_dict.has_key("ip")):
				break
			i+=1
		#add node
		hop_dict=parse_hop(hop_list[i])
		ip=hop_dict["ip"]
		rtt_i=hop_dict["rtt"]
		node_i=model.Node(ip)
		ind_i=graph.add_node(node_i)
		while i<=len(hop_list)-1:
			j=i+1
			is_direct=True
			while (j<len(hop_list)):
				hop_dict=parse_hop(hop_list[j])
				if (hop_dict.has_key("ip")):
					break
				is_direct=False
				j+=1
			#print "i:%s, j:%s" % (i, j) #debug
			
			#print "ip:%s, ind_i:%s" % (ip, ind_i) #debug
			if i==len(hop_list)-1 and dst_ip==ip: #check if hop is host.
				#print "is not router" #debug
				graph.nodes[ind_i].is_router=False

			if j<len(hop_list):
				hop_dict=parse_hop(hop_list[j])
				ip=hop_dict["ip"]
				rtt_j=hop_dict["rtt"]
				node_j=model.Node(ip)
				ind_j=graph.add_node(node_j)
				#print "ip:%s, ind_i:%s" % (ip, ind_i) #debug
				if j==len(hop_list)-1 and dst_ip==ip: #check if hop is host.
					#print "is not router" #debug
					graph.nodes[ind_j].is_router=False

				if not is_direct:
					blank=(ind_i,j-i-1,ind_j)
					node_blank=model.Node(blank)
					node_blank.is_blank=True
					ind_blank=graph.add_node(node_blank)
				
				#add edge
				delay=rtt_j-rtt_i
				edge=model.Edge(ind_i, ind_j, delay)
				edge.is_direct=is_direct
				graph.add_edge(edge)
		
			rtt_i=rtt_j
			ind_i=ind_j
			i=j

def usage():
	print "python router.py <data_dir>"

def main(argv):
	if len(argv) < 2:
		usage()
		exit()
	
	data_dir=argv[1]
	build_graph(data_dir)

if __name__ == "__main__":
	main(sys.argv)
