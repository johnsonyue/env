import sys
import time
import math

import trace

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

def insert_edge(edge,src,dst):
	if(edge.has_key((src,dst))):
		edge[(src,dst)]+=1
	else:
		edge[(src,dst)]=0

def build_graph():
	node={}
        edge={}
        tm = time.time()
        while True:
                try:
                        prev_node = -1
                        line = raw_input()
                        if ( line.split(trace.header_delimiter)[0] == trace.header_indicator ):
                                t = time.time()
                                sys.stderr.write( "%s,%s,%s\n" % (line, t, t-tm) )
                                tm = t
                                continue

                        field_list = line.split(trace.field_delimiter)
                        dst_ip = field_list[ trace.trace_index["dst_ip"] ]
                        #timestamp = field_list[ trace.trace_index["timestamp"] ]
                        hops = field_list[ trace.trace_index["hops"] ]
                        hop_list = hops.split(trace.hop_delimiter)
                        for i in range(len(hop_list)):
				h=hop_list[i]
                                if h == trace.blank_holder:
					if (prev_node!=-1):
						insert_edge(edge,prev_node,-1)
					prev_node=-1
                                        continue #ignores blank
                                reply_list = h.split(trace.reply_delimiter)
                                first_reply = reply_list[0]
                                ip = first_reply.split(trace.ip_delimiter)[trace.hop_index["ip"]]
				ind=ip2int(ip)
				if ( i == len(hop_list)-1 and ip==dst_ip ):
					node[ind] = "t"
				elif (not node.has_key(ind) ):
					node[ind] = "r"

				insert_edge(edge,prev_node,ind)
                                prev_node = ind
                except EOFError:
                        sys.stderr.write("OUTPUT\n")
                        printg(node,edge)

                        break
		except Exception, e:
			print e

def printg(node, edge):
        print "%s %s" % ( len(node), len(edge) )
        for i,t in node.items():
                print "%s, %s"%(int2ip(i),t)
        for e,c in edge.items():
                print "%s %s %s" % ( int2ip(e[0]), int2ip(e[1]), c )

if __name__ == "__main__":
        build_graph()
