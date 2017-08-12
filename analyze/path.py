from sets import Set

def line_cmp(line1, line2):
	ip1=line1.split(' ')[1]
	ip2=line2.split(' ')[1]
	return ip_cmp(ip1, ip2)

def ip_cmp(ip1,ip2):
	fields1=ip1.split('.')
	fields2=ip2.split('.')
	for i in range(len(fields1)):
		if int(fields1[i])>int(fields2[i]):
			return 1
		elif int(fields1[i])<int(fields2[i]):
			return -1
	return 0

def bin_search(edge_list, src):
	h=len(edge_list)-1
	l=0
	m=(h+l)/2
	while h>=l:
		esrc=edge_list[m].split(' ')[0]
		if esrc == src:
			return m
		elif esrc>src:
			h=m-1
		elif esrc<src:
			l=m+1
		m=(h+l)/2
	
	return -1

def search(edge_list, src):
	for i in range(len(edge_list)):
		esrc=edge_list[i].split(' ')[0]
		if esrc==src:
			return i
	return -1
		

def graph_to_paths(edge_file_name):
	fp=open(edge_file_name,'rb')
	edge_list=[]
	print "edge_list ... ",
	while True:
		line=fp.readline()
		if not line:
			break
		edge_list.append(line.strip('\n'))
	print "done"

	#out degree list
	print "outdegree ... ",
	out_deg_dict={}
	i=0
	deg=0
	while True:
		i+=1
		if i<=len(edge_list)-1:
			e=edge_list[i].split(' ')[0]
		deg+=1
		if e!=edge_list[i-1].split(' ')[0] or (i==len(edge_list)):
			out_deg_dict[edge_list[i-1].split(' ')[0]]=deg
			deg=0
			if i==len(edge_list):
				break
	print "done"

	print "rev_list ... ",
	rev_list=sorted(edge_list, cmp=line_cmp)
	print "done"

	#print "rev_list:" #debug
	#for l in rev_list:
	#	print l
	
	#in degree list
	print "indegree ...",
	in_deg_dict={}
	i=0
	deg=0
	while True:
		i+=1
		if i<=len(edge_list)-1:
			e=edge_list[i].split(' ')[1]
		deg+=1
		if e!=edge_list[i-1].split(' ')[1] or (i==len(edge_list)):
			in_deg_dict[edge_list[i-1].split(' ')[1]]=deg
			deg=0
			if i==len(edge_list):
				break
	print "done"
	
	src_list=[ k for k in out_deg_dict.keys() if (not in_deg_dict.has_key(k)) ]
	dst_list=[ k for k in in_deg_dict.keys() if (not out_deg_dict.has_key(k)) ]
	
	#print src_list
	#print dst_list
	#print "in_deg_dict:"
	#for k,v in in_deg_dict.items():
	#	print k,v
	#print "out_deg_dict:"
	#for k,v in out_deg_dict.items():
	#	print k,v
	
		
	dst_set=Set(dst_list)
	
	path_list=[]
	#edge to path
	for s in src_list:
		
		while True:
			is_finished=False
			root=s
			path=[]
			visited=Set(root)
			ind=search(edge_list,root)
			if ind==-1:
				is_finished=True
				break
			while True:
				ind=bin_search(edge_list,root)
				e=edge_list[ind]
				dst=e.split(' ')[1]
				num = int(e.split(' ')[-1])
				path.append(e)
				if num == 1:
					del edge_list[ind]
				else:
					edge_list[ind]=e.rsplit(' ',1)[0]+" "+str(num-1)

				if (dst in dst_set) or (dst in visited):
					print path[0].split(' ')[0],path[0].split(' ')[1],
					for p in path[1:]:
						print p.split(' ')[1],
					print 
					path_list.append(path)
					break
				visited.add(dst)
				
				root=dst
			
			if is_finished:
				break
	
	print len(path_list)
	#print "edge_list:"
	#for e in edge_list:
	#	print e

graph_to_paths("shit")
