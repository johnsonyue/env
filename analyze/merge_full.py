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

def merge(file1, file2, file_out):
	#open files.
	fp1 = open(file1, 'r')
	line1=fp1.readline()
	num_node1=int(line1.split(' ')[0])
	num_edge1=int(line1.split(' ')[1])

	fp2=open(file2,'r')
	line2=fp2.readline()
	num_node2=int(line2.split(' ')[0])
	num_edge2=int(line2.split(' ')[1])
	
	file_out_temp=file_out+".temp"
	fpot=open(file_out_temp,'w')
	
	#merge node.
	node_cnt=0
	edge_cnt=0

	line1=fp1.readline()
	line2=fp2.readline()
	while (num_node1>0 and num_node2>0):
		cmp = node_line_cmp(line1,line2)
		if (cmp < 0):
			fpot.write(line1)
			num_node1-=1
			line1=fp1.readline()
		elif (cmp > 0):
			fpot.write(line2)
			num_node2-=1
			line2=fp2.readline()
		else:
			fpot.write(line1)
			num_node1-=1
			num_node2-=1
			line1=fp1.readline()
			line2=fp2.readline()
		node_cnt+=1
		
	while (num_node1>0):
		fpot.write(line1)
		num_node1-=1
		line1=fp1.readline()
		node_cnt+=1
		
	while (num_node2>0):
		fpot.write(line2)
		num_node2-=1
		line2=fp2.readline()
		node_cnt+=1
	
	#merge edge
	while (num_edge1>0 and num_edge2>0):
		cmp = edge_line_cmp(line1,line2)
		if (cmp < 0):
			fpot.write(line1)
			num_edge1-=1
			line1=fp1.readline()
		elif (cmp > 0):
			fpot.write(line2)
			num_edge2-=1
			line2=fp2.readline()
		else:
			edge_field=line1.split(' ')[:-1]
			edge_num1=int(line1.split(' ')[-1])
			edge_num2=int(line2.split(' ')[-1])
			line=edge_field[0]+" "+edge_field[1]+" "+str(edge_num1+edge_num2)+"\n"
			fpot.write(line)
			num_edge1-=1
			num_edge2-=1
			line1=fp1.readline()
			line2=fp2.readline()
		edge_cnt+=1

	while (num_edge1>0):
		fpot.write(line1)
		num_edge1-=1
		line1=fp1.readline()
		edge_cnt+=1

	while (num_edge2>0):
		fpot.write(line2)
		num_edge2-=1
		line2=fp2.readline()
		edge_cnt+=1
	fpot.close()

	fpot=open(file_out_temp,'r')
	fpo=open(file_out,'w')
	fpo.write( "%s %s\n" % (node_cnt, edge_cnt) )
	fpo.write(fpot.read())

	#clear up.
	fp1.close()
	fp2.close()
	fpot.close()
	fpo.close()
	
	os.remove(file_out_temp)

def gunzip(data_dir):
	file_list = os.popen( "ls %s/*.gz" % (data_dir) ).readlines()
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
	file_list = gunzip(data_dir)
	
	prev_file_list=[]
	while (len(file_list)>1):
		temp_file_list=[]
		for i in range(len(file_list)/2):
			out_file="%s.%s.out" % (len(file_list), i)
			print ("merge %s %s into %s" % (data_dir+"/"+file_list[2*i], data_dir+"/"+file_list[2*i+1], data_dir+"/"+out_file)),
			sys.stdout.flush()
			merge(data_dir+"/"+file_list[2*i], data_dir+"/"+file_list[2*i+1], data_dir+"/"+out_file)
			print "done"
			temp_file_list.append(out_file)
		#remember to handle the odd.
		if (len(file_list)%2 != 0):
			out_file="%s.%s.out" % (len(file_list), len(file_list)/2)
			print ("merge %s into %s" % (data_dir+"/"+file_list[len(file_list)-1], data_dir+"/"+out_file)),
			sys.stdout.flush()
			os.system( "cp %s %s" % (data_dir+"/"+file_list[len(file_list)-1], data_dir+"/"+out_file) )
			print "done"
			temp_file_list.append(out_file)

		for i in range(len(prev_file_list)):
			os.remove(data_dir+"/"+prev_file_list[i])
		
		prev_file_list=file_list
		file_list=temp_file_list

	for i in range(len(prev_file_list)):
		os.remove(data_dir+"/"+prev_file_list[i])

if __name__ == "__main__":
	main(sys.argv)
