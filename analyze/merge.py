import sys
import os

def merge(file1, file2, file_out):
	#open files.
	fp1=open(file1,'r')
	line1=fp1.readline()
	num_node1=int(line1.split(' ')[0])
	num_edge1=int(line1.split(' ')[1])

	fp2=open(file2,'r')
	line2=fp2.readline()
	num_node2=int(line2.split(' ')[0])
	num_edge2=int(line2.split(' ')[1])
	
	file_out_temp=file_out+".temp"
	fpot=open(file_out_temp,'w')
	
	#merge.
	node_cnt=0
	edge_cnt=0
	if num_node1>0:
		line1=fp1.readline()
	if num_node2>0:
		line2=fp2.readline()
	while (num_node1>0 and num_node2>0):
		if (line1 < line2):
			fpot.write(line1)
			line1=fp1.readline()
			num_node1-=1
		elif (line1 > line2):
			fpot.write(line2)
			line2=fp2.readline()
			num_node2-=1
		else:
			fpot.write(line1)
			line1=fp1.readline()
			line2=fp2.readline()
			num_node1-=1
			num_node2-=1
		node_cnt+=1
		
	while (num_node1>0):
		fpot.write(line1)
		line1=fp1.readline()
		num_node1-=1
		node_cnt+=1
		
	while (num_node2>0):
		fpot.write(line2)
		line2=fp2.readline()
		num_node2-=1
		node_cnt+=1
	
	if num_edge1>0:
		line1=fp1.readline()
	if num_edge2>0:
		line2=fp2.readline()
	while (num_edge1>0 and num_edge2>0):
		if (line1 < line2):
			fpot.write(line1)
			line1=fp1.readline()
			num_edge1-=1
		elif (line1 > line2):
			fpot.write(line2)
			line2=fp2.readline()
			num_edge2-=1
		else:
			fpot.write(line1)
			line1=fp1.readline()
			line2=fp2.readline()
			num_edge1-=1
			num_edge2-=1
		edge_cnt+=1

	while (num_edge1>0):
		fpot.write(line1)
		line1=fp1.readline()
		num_edge1-=1
		edge_cnt+=1

	while (num_edge2>0):
		fpot.write(line2)
		line2=fp2.readline()
		num_edge2-=1
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

def usage():
	print "python merge.py dir"

def main(argv):
	if len(argv) < 2:
		usage()
		exit()

	data_dir=argv[1]
	file_list = os.popen( "ls %s" % (data_dir) ).readlines()
	file_list = map(lambda x:x.strip('\n'), file_list)
	
	prev_file_list=[]
	is_origin=True
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
		
		if (not is_origin):
			prev_file_list=file_list
		is_origin = False
		file_list=temp_file_list

	for i in range(len(prev_file_list)):
		os.remove(data_dir+"/"+prev_file_list[i])

if __name__ == "__main__":
	main(sys.argv)
