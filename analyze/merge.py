import sys
import os
import re

def ip2int(ip):
	r=3
	i=0
	for o in ip.split('.'):
		o=int(o)
		i+=o*pow(256,r)
		r-=1
	
	return i

def node_line_cmp(line1, line2):
	line1=line1.split(', ')[0]
	line2=line2.split(', ')[0]
	if (re.findall("\(",line1)):
		if (not re.findall("\(",line2)):
			return 1
		else:
			tuple1=line1.replace("(","").replace(")","").split(',')[:2]
			tuple1=map(lambda x:ip2int(x), tuple1)
			tuple2=line2.replace("(","").replace(")","").split(',')[:2]
			tuple2=map(lambda x:ip2int(x), tuple2)
			if ( tuple1[0] != tuple2[0] ):
				return tuple1[0] - tuple2[0]
			else:
				return tuple1[1] - tuple2[1]
	else:
		if (re.findall("\(",line2)):
			return -1
		else:
			return ip2int(line1)-ip2int(line2)
			
def edge_line_cmp(line1, line2):
	tuple1=line1.split(' ')
	tuple2=line2.split(' ')
	if node_line_cmp(tuple1[0], tuple2[0]) != 0:
		return node_line_cmp(tuple1[0], tuple2[0])
	else:
		return node_line_cmp(tuple1[1], tuple2[1])

def merge_node(file1, file2, file_out):
	#open files.
	fp1 = open(file1, 'r')
	fp2=open(file2,'r')
	
	file_out_temp=file_out+".temp"
	fpo=open(file_out,'w')
	
	#merge node.
	node_cnt=0

	line1=fp1.readline()
	line2=fp2.readline()
	while (line1!='' and line2!=''):
		cmp = node_line_cmp(line1,line2)
		if (cmp < 0):
			fpo.write(line1)
			line1=fp1.readline()
		elif (cmp > 0):
			fpo.write(line2)
			line2=fp2.readline()
		else:
			fpo.write(line1)
			line1=fp1.readline()
			line2=fp2.readline()
		node_cnt+=1
		
	while (line1!=''):
		fpo.write(line1)
		line1=fp1.readline()
		node_cnt+=1
		
	while (line2!=''):
		fpo.write(line2)
		line2=fp2.readline()
		node_cnt+=1
	
	fpo.close()

	#clear up.
	fp1.close()
	fp2.close()
	fpo.close()
	
	return node_cnt
	
def merge_edge(file1, file2, file_out):
	#open files.
	fp1 = open(file1, 'r')
	fp2=open(file2,'r')
	fpo=open(file_out,'w')

	#merge edge
	edge_cnt=0
	
	line1=fp1.readline()
	line2=fp2.readline()
	while (line1!='' and line2!=''):
		cmp = edge_line_cmp(line1,line2)
		if (cmp < 0):
			fpo.write(line1)
			line1=fp1.readline()
		elif (cmp > 0):
			fpo.write(line2)
			line2=fp2.readline()
		else:
			edge_field=line1.split(' ')[0:2]
			#edge_num1=int(line1.split(' ')[2])
			#edge_num2=int(line2.split(' ')[2])
			edge_type1=line1.split(' ')[2]
			edge_type2=line2.split(' ')[2]
			tp="I"
			if edge_type1=="D" or edge_type2=="D":
				tp="D"
			delay1=float(line1.split(' ')[3])
			delay2=float(line2.split(' ')[3])
			delay=delay1 if delay1 < delay2 else delay2
			line="%s %s %s %s\n" % (edge_field[0], edge_field[1], tp, delay)
			fpo.write(line)
			line1=fp1.readline()
			line2=fp2.readline()
		edge_cnt+=1

	while (line1!=''):
		fpo.write(line1)
		line1=fp1.readline()
		edge_cnt+=1

	while (line2!=''):
		fpo.write(line2)
		line2=fp2.readline()
		edge_cnt+=1

	#clear up.
	fp1.close()
	fp2.close()
	fpo.close()
	
	return edge_cnt
	
def gunzip(data_dir,file_type):
	file_list = os.popen( "ls %s/*%s.gz" % (data_dir, file_type) ).readlines()
	file_list = map(lambda x:x.strip('\n').split('/')[-1], file_list)
	ret_list = []
	for f in file_list:
		os.system("gzip -kdf %s" % (data_dir+"/"+f))
		ret_list.append(f.strip(".gz"))
	
	return ret_list

def usage():
	print "python merge.py dir"

def main(argv):
	if len(argv) < 2:
		usage()
		exit()

	data_dir=argv[1]
	node_list = gunzip(data_dir,"node")
	edge_list = gunzip(data_dir,"link")
	
	prev_node_list=[]
	prev_edge_list=[]
	while (len(node_list)>1):
		temp_node_list=[]
		temp_edge_list=[]
		for i in range(len(node_list)/2):
			out_node_file="%s.%s.node.out" % (len(node_list), i)
			out_edge_file="%s.%s.edge.out" % (len(edge_list), i)
			print ("merge %s %s into %s" % (data_dir+"/"+node_list[2*i], data_dir+"/"+node_list[2*i+1], data_dir+"/"+out_node_file)),
			sys.stdout.flush()
			merge_node(data_dir+"/"+node_list[2*i], data_dir+"/"+node_list[2*i+1], data_dir+"/"+out_node_file)
			merge_edge(data_dir+"/"+edge_list[2*i], data_dir+"/"+edge_list[2*i+1], data_dir+"/"+out_edge_file)
			print "done"
			temp_node_list.append(out_node_file)
			temp_edge_list.append(out_edge_file)
		#remember to handle the odd.
		if (len(node_list)%2 != 0):
			out_node_file="%s.%s.node.out" % (len(node_list), len(node_list)/2)
			out_edge_file="%s.%s.edge.out" % (len(edge_list), len(edge_list)/2)
			print ("merge %s into %s" % (data_dir+"/"+node_list[len(node_list)-1], data_dir+"/"+out_node_file)),
			sys.stdout.flush()
			os.system( "cp %s %s" % (data_dir+"/"+node_list[len(node_list)-1], data_dir+"/"+out_node_file) )
			os.system( "cp %s %s" % (data_dir+"/"+edge_list[len(edge_list)-1], data_dir+"/"+out_edge_file) )
			print "done"
			temp_node_list.append(out_node_file)
			temp_edge_list.append(out_edge_file)

		for i in range(len(prev_node_list)):
			os.remove(data_dir+"/"+prev_node_list[i])
			os.remove(data_dir+"/"+prev_edge_list[i])
		
		prev_node_list=node_list
		prev_edge_list=edge_list
		node_list=temp_node_list
		edge_list=temp_edge_list

	for i in range(len(prev_node_list)):
		os.remove(data_dir+"/"+prev_node_list[i])
		os.remove(data_dir+"/"+prev_edge_list[i])

if __name__ == "__main__":
	main(sys.argv)
