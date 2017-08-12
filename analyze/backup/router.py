import sys
import os
import time
import math
import subprocess

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

def insert_edge(edge,src,dst,delay):
	if(edge.has_key((src,dst))):
		edge[(src,dst)][0]+=1
		if (edge[(src,dst)][1] > delay):
			edge[(src,dst)][1]=delay #use the minimal delay
	else:
		edge[(src,dst)]=[1,delay]

def store(team, date, true_date, monitor, node, edge, data_dir):
	path="%s/%s"%(data_dir,date)
	if ( not os.path.exists(path) ):
		os.makedirs(path)
	
	fn="%s/%s.%s.%s.node.gz" % (path,team,true_date,monitor)
	fn2="%s/%s.%s.%s.link.gz" % (path,team,true_date,monitor)
	fp=open(fn,'w')
	fp2=open(fn2,'w')
	h = subprocess.Popen(['gzip', '-c', '-'], stdin=subprocess.PIPE, stdout=fp)
	h2 = subprocess.Popen(['gzip', '-c', '-'], stdin=subprocess.PIPE, stdout=fp2)
	
        for i in sorted( node.iterkeys() ):
		t=node[i]
		h.stdin.write( "%s, %s\n" % ( node2str(i), t ) )
        for e,c in sorted(edge.iteritems(), key=lambda (k,v):(k[0],k[1])):
                h2.stdin.write( "%s %s %s %s\n" % ( node2str(e[0]), node2str(e[1]), c[0], c[1] ) )
	h.stdin.close()
	h2.stdin.close()

def build_graph(data_dir):
	node={}
        edge={}
        tm = time.time()
	
	team=""
	date=""
	true_date=""
	monitor=""
        while True:
                try:
                        prev_node = -1
                        prev_rtt = -1
                        line = raw_input()
                        if ( line.split(trace.header_delimiter)[0] == trace.header_indicator ):
                                t = time.time()
                                sys.stderr.write( "%s,%s,%s\n" % (line, t, t-tm) )
                                tm = t

				#output
				if (team and date and true_date and monitor):
					store(team, date, true_date, monitor, node, edge, data_dir)
					node={}
					edge={}
				#update team,date,monitor
				fields_list=line.split(trace.header_delimiter)[1:]
				team=fields_list[trace.header_index["team"]]
				true_date=fields_list[trace.header_index["true_date"]]
				date=fields_list[trace.header_index["date"]]
				monitor=fields_list[trace.header_index["monitor"]]
                                continue

                        field_list = line.split(trace.field_delimiter)
                        dst_ip = field_list[ trace.trace_index["dst_ip"] ]
                        #timestamp = field_list[ trace.trace_index["timestamp"] ]
                        hops = field_list[ trace.trace_index["hops"] ]
                        temp_hop_list = hops.split(trace.hop_delimiter)

			hop_list=[]
			for i in range(len(temp_hop_list)): #ignore blank prefix.
				if ( temp_hop_list[i]==trace.blank_holder):
					continue
				else:
					hop_list=temp_hop_list[i:]
					break
			if (len(hop_list) == 0): #do nothing if all blank.
				continue
			
			blank_cnt = 0
			reply_list = hop_list[0].split(trace.reply_delimiter)
			first_reply = reply_list[0]
			ip = first_reply.split(trace.ip_delimiter)[trace.hop_index["ip"]]
			rtt = float(first_reply.split(trace.ip_delimiter)[trace.hop_index["rtt"]])
			node_blank = -1
			rtt_blank = -1
                        for i in range(len(hop_list)):
				h=hop_list[i]
                                if h == trace.blank_holder:
					blank_cnt+=1
					prev_node=-1
					prev_rtt=-1
                                        continue #blank
                                reply_list = h.split(trace.reply_delimiter)
                                first_reply = reply_list[0]
                                ip = first_reply.split(trace.ip_delimiter)[trace.hop_index["ip"]]
                                rtt = float(first_reply.split(trace.ip_delimiter)[trace.hop_index["rtt"]])
				ind=ip2int(ip)
				if ( i == len(hop_list)-1 and ip==dst_ip ): #if target is reached 
					node[ind] = "t"
				elif (not node.has_key(ind) ):
					node[ind] = "r"
				
				if ( prev_node == -1 and node_blank != -1): #if prev is blank
					blank=(node_blank,blank_cnt,ind)
					node[blank] = "r"
					delay=rtt-rtt_blank
					insert_edge(edge,node_blank,blank,rtt_blank/2)
					insert_edge(edge,blank,ind,rtt_blank/2) #divide in halves
				elif ( prev_node != -1):
					delay=rtt-prev_rtt
					insert_edge(edge,prev_node,ind,delay)

                                prev_node = ind
				prev_rtt = rtt
				node_blank = ind
				rtt_blank = rtt
                except EOFError:
			store(team, date, true_date, monitor, node, edge, data_dir)

                        break
		except Exception, e:
			print e
			break

def node2str(n):
	if type(n) == type(1):
		return int2ip(n)
	return "(%s,%s,%s)" % (int2ip(n[0]), n[1], int2ip(n[2]))

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
