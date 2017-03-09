import os
import re
import time

#time utils.
def is_heap_year(year):
	if (not year % 400 or not year % 4):
		return True
	return False

def days_in_month(year, month):
	m2d = [0,31,28,31,30,31,30,31,31,30,31,30,31]

	return m2d[month]+(1 if month == 2 and is_heap_year(year) else 0)

def next_day(date):
	y=int(date[:4])
	m=int(date[4:6])
	d=int(date[6:8])
	
	num = days_in_month(y,m)
	if (d+1 > num):
		m = m + 1
		d = 1
		if (m > 12):
			y = y + 1
			m = 1
	else:
		d = d + 1
	
	str = "%d%02d%02d" % (y, m, d)
	return str

def update_state_file(file_name, end_time, start_time="", is_init = False):
	if (is_init):
		if (re.findall('/',file_name)):
			dir = file_name.rsplit('/',1)[0]
			if( not os.path.exists(dir) ):
				os.makedirs(dir)
		if (not os.path.exists(file_name)):
			open(file_name,'wb').close()
		if (start_time == ""):
			print "must provide start_time"
			exit()
	
		st = start_time
		#while(is_occupied(file_name)):
		#	time.sleep(random.randint(1,3))
		fp = open(file_name, 'wb')
	
	else:
		if (not os.path.exists(file_name)):
			print ("file does not exist")
			exit()

		#while(is_occupied(file_name)):
		#	time.sleep(random.randint(1,3))
		fp = open(file_name,'r')
		st = fp.readlines()[-1].split(' ')[0]
		st = next_day(st)
		fp.close()

		#while(is_occupied(file_name)):
		#	time.sleep(random.randint(1,3))
		fp = open(file_name,'a')
	
	y = int(st[:4])
	m = int(st[4:6])
	d = int(st[6:8])

	ey = int(end_time[:4])
	em = int(end_time[4:6])
	ed = int(end_time[6:8])
	
	while ( y < ey ):
		while ( m <= 12 ):
			num = days_in_month(y, m)
			while( d <= num ):
				str = "%d%02d%02d" % (y, m, d)
				fp.write(str+" unassigned"+'\n')
				d = d + 1
			d = 1
			m = m + 1
		m = 1
		y = y + 1
	
	while ( m < em ):
		num = days_in_month(ey, m)
		while ( d <= num ):
			str = "%d%02d%02d" % (y, m, d)
			fp.write(str+" unassigned"+'\n')
			d = d + 1
		d = 1
		m = m + 1
	
	while ( d <= ed ):
		str = "%d%02d%02d" % (y, m, d)
		fp.write(str+" unassigned"+'\n')
		d = d + 1

	fp.close()

def update_path_state_file(file_name, data_dir, is_init=False):
	if ( is_init ):
		if (re.findall('/',file_name)):
			dir = file_name.rsplit('/',1)[0]
			if( not os.path.exists(dir) ):
				os.makedirs(dir)
		fp = open(file_name,'wb')

		for dir in os.popen("ls -1A %s | sort" % (data_dir)).readlines():
			dir = dir.strip('\n')
			if ( re.findall("^\d{8}$", dir) ):
				if ( len(os.popen("ls -1A %s/%s" % (data_dir, dir)).readlines()) ): #not empty
					fp.write("%s unassigned\n" % dir)
		exit()

	#not init
	if (not os.path.exists(file_name)):
		sys.stderr.write( "%s not found\n" % (file_name) )
		exit()
	flines = open(file_name,'rb').readlines()
	dirs = []
	fp = open(file_name,'wb')
	for dir in os.popen("ls -1A %s | sort" % (data_dir)).readlines():
		dir = dir.strip('\n')
		if ( re.findall("^\d{8}$", dir) ): #yyyymmdd
			if ( len(os.popen("ls -1A %s/%s" % (data_dir, dir)).readlines()) ): #not empty
				dirs.append(dir)
	#merge
	i=0; j=0
	while ( i < len(flines) and j < len(dirs) ):
		fdir = flines[i].split(' ')[0]
		if (fdir == dirs[j]):
			fp.write("%s\n" % (flines[i].strip('\n')))
			i += 1
			j += 1
		elif (dirs[j] < fdir):
			fp.write("%s unassigned\n" % (dirs[j]))
			j += 1
		else:
			fp.write("%s deleted\n" % (fdir))
			i += 1
	while ( i < len(flines) ):
		fp.write("%s deleted\n" % (flines[i].split(' ')[0]))
		i += 1
	while ( j < len(dirs) ):
		fp.write("%s unassigned\n" % (dirs[j]))
		j += 1

def auth_node(secret_file, node_id, node_key): #primitive, will be replaced
	fp = open(secret_file,'r')
	for line in fp.readlines():
		list = line.split(' ')
		if (list[0] == node_id and list[1].strip('\n') == node_key):
			fp.close()
			return True
	
	fp.close()
	return False
			
#enum state={finished, unassigned, pending, terminated}
def change_state(file_name, date, state):
	#while(is_occupied(file_name)):
	#		time.sleep(random.randint(1,3))
	fp = open(file_name, 'r')
	lines = fp.readlines()
	fp.close()

	#while(is_occupied(file_name)):
	#		time.sleep(random.randint(1,3))
	fp = open(file_name, 'w')
	for line in lines:
		if (line.split(' ')[0] == date):
			fp.write(date+" "+state+'\n')
		else:
			fp.write(line)
	fp.close()

def get_task(file_name):
	#while(is_occupied(file_name)):
	#		time.sleep(random.randint(1,3))
	fp = open(file_name, 'r')
	lines = fp.readlines()
	res = ""
	for i in range(len(lines)-1, -1, -1):
		state = lines[i].split(' ')[1].strip('\n')
		if(state != "finished" and state != "pending" and state != "deleted"):
			res = lines[i].split(' ')[0]
			break
		
	return res

def on_notify(log_file_name, state_file_name, notify_type, args):
	#while(is_occupied(log_file_name)):
	#		time.sleep(random.randint(1,3))
	fp = open(log_file_name, 'a')
	strftime = time.strftime("%Y-%m-%d %H:%M:%S")
	result_str = ""
	result_str += notify_type
	
	if (notify_type == "finished"):
		node_id = args["node_id"]
		task = args["task"]
		time_used = args["time_used"]

		change_state(state_file_name, task, "finished")
		result_str = "%s %s %s finished, time used: %s(s)\n" % (strftime, node_id, task, time_used) 
		fp.write(result_str)
	elif (notify_type == "started"):
		node_id = args["node_id"]
		task = args["task"]

		change_state(state_file_name, task, "pending")
		result_str = "%s %s %s started\n" % (strftime, node_id, task)
		fp.write(result_str)
	elif (notify_type == "terminated"):
		node_id = args["node_id"]
		task = args["task"]

		change_state(state_file_name, task, "terminated")
	
		result_str = "%s %s %s terminated\n" % (strftime, node_id, task)
		fp.write(result_str)

	fp.close()
	
	return result_str
