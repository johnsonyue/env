import sys
from sets import Set

def oct2bin(octet):
		result = []
		for i in range(8):
			result.append(0)
		
		for i in range(8):
			result[i] = octet % 2
			octet = octet / 2
		
		result.reverse()
		return result

def in_subnet(ip, pfx_str):
	pfx_fields=pfx_str.split('/')
	pfx_octs=pfx_fields[0].split('.')
	mask=int(pfx_fields[1])
	ip_octs=ip.split('.')
	
	#compare octet-wise
	q=mask/8
	for i in range(q):
		if (pfx_octs[i]!=ip_octs[i]):
			return False

	#remaining bits
	r=mask%8
	pfx_ro=oct2bin(int(pfx_octs[q]))
	ip_ro=oct2bin(int(ip_octs[q]))
	for i in range(r):
		if (pfx_ro[i]!=ip_ro[i]):
			return False
	
	return True
		
def is_reserved(ip):
	#16 reserved IP address segments. (ref: wiki)
	reserved_list = [
		"0.0.0.0/8",
		"224.0.0.0/4",
		"240.0.0.0/4",
		"0.0.0.0/8",
		"10.0.0.0/8",
		"127.0.0.0/8",
		"100.64.0.0/10",
		"172.16.0.0/12",
		"198.18.0.0/15",
		"169.254.0.0/16",
		"192.168.0.0/16",
		"192.0.0.0/24",
		"192.0.2.0/24",
		"192.88.99.0/24",
		"192.51.100.0/24",
		"203.0.113.0/24",
		"255.255.255.255/32"
	]
	
	for r in reserved_list:
		if (in_subnet(ip,r)):
			return True
	return False

#debug
def test():
	test=["114.114.114.114","192.168.1.2","172.17.0.2","255.255.0.0","202.118.236.224","173.26.103.12","192.18.20.1","198.18.20.1","0.0.0.1"]
	
	for t in test:
		print "%s, %s" % (t, is_reserved(t))

def ip_cmp(ip1,ip2):
	fields1=ip1.split('.')
	fields2=ip2.split('.')
	for i in range(len(fields1)):
		if int(fields1[i])>int(fields2[i]):
			return 1
		else:
			return -1
	return 0

#find both connected components
def bcc(edge_list): #bfs
	print "initializing ... ", #debug
	visited=[False for i in range(len(edge_list))]
	print "done."
	cc_list=[]
	while True:
		cc=[]
		finished=True
		#print visited #debug
		for i in range(len(edge_list)): #find unvisited edge
			if not visited[i]:
				visited[i]=True
				finished=False
				break
		if finished:
			break

		#perform BFS
		e=edge_list[i]
		nodes=Set([e.split(' ')[0], e.split(' ')[1]])
		cc.append(e)
		while True:
			has_new=False
			for i in range(len(edge_list)):
				if not visited[i]:
					e=edge_list[i]
					es=e.split(' ')[0]
					et=e.split(' ')[1]
					if (es in nodes) or (et in nodes):
						visited[i]=True
						has_new=True
						nodes.add(es)
						nodes.add(et)
						cc.append(e)
			if not has_new:
				cc_list.append(cc)
				break
	return cc_list

def expand_bcc():
	return

def initial_partition(edge_file_name):
	#open edge file.
	try:
		fp=open(edge_file_name,'rb')
	except:
		sys.stderr.write("Failed to open file: %s\n" % (edge_file_name))
		return

	#initialization.
	bcc_fn=None
	ie_fn=None #bcc and inter edge kept in **HardDrive**
	octet=-1 #state variable to bookkeep current address space.

	edge_list=[] #edge list kept in **RAM**
	
	#kickstart first line
	line=fp.readline()
	if not line:
		sys.stderr.write("Empty edge file provided\n")
	
	while True:
		fields=line.split(' ')
		src=fields[0]
		dst=fields[1]
		
		#if reserved ip or long hauls, ignore.
		if is_reserved(src) or is_reserved(dst):
			continue
		delay=float(fields[3])
		if delay > 5 or delay < -10:
			continue
		
		#elif address space is full, 
		#directly get bcc from RAM,
		#then merge into bcc kept in HD
		first_oct=int(src.split('.')[0])
		if first_oct - octet >= 20:
			bcc()
			if bcc_fn:
				expand_bcc()
			continue #don't read new line yet
		
		#else, add line to edge_list (RAM)
		edge_list.append(line)

		line=fp.readline()
		if not line:
			if len(edge_list) != 0: #handle residue edge list
				bcc()
				if bcc_fn:
					expand_bcc()
			break
	
	#output
	output_partitions()

def test2():
	'''
	edge_list=[
		"1 2 1 D",
		"2 3 1 D",
		"2 4 1 D",
		"3 13 1 D",
		"4 12 1 D",
		"5 2 1 D",
		"6 8 1 D",
		"7 1 1 D",
		"9 11 1 D",
		"10 6 1 D"
	]
	'''
	fp=open("2.0.edge.out")
	edge_list=map(lambda x:x.strip('\n'), fp.readlines())
	
	cc_list=connected_component(edge_list)
	print 
	print len(cc_list)

def test3():
	return

def main():
	#debug.
	#test()
	#test2()
	initial_partition("2.0.edge.out")

if __name__ == "__main__":
	main()
