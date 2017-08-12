import sys
import re

import trace

#uniform caida.
def build_hops(hops_field, replied, dst_ip, dst_rtt):
	hop_list = hops_field.split('\t')
	hops = ""
	for i in range(len(hop_list)):
		h = []
		if (hop_list[i] == "q"):
			hops += trace.build_hop_str(h)+trace.hop_delimiter #uses hop format in trace.
			continue

		#each hop could consist of up to 3 replies.
		reply_list = hop_list[i].split(';')
		for j in range(len(reply_list)):
			fields = reply_list[j].split(',')
			ip = fields[0]
			rtt = fields[1]
			ntries = fields[2]
			h.append( (ip, rtt, ntries) )
		hops += trace.build_hop_str(h)+trace.hop_delimiter #uses hop format in trace.
	
	#append dst_ip to the end if replied.
	h = []
	if (replied=='R'):
		ip = dst_ip
		rtt = dst_rtt
		nTries = "1"
		h.append( (ip, rtt, ntries) )
		hops += trace.build_hop_str(h)+trace.hop_delimiter #uses hop format in trace.

	return hops.strip(trace.hop_delimiter)

def uniform_caida():
	sys.stderr.write("Message: started parsing caida...\n")
	is_header_updated = False
	header=""
	while True:
		try:
			line=raw_input()
			if (line.split(trace.header_delimiter)[0] == trace.header_indicator): #header
				header=line.split(trace.header_delimiter,1)[1]
				is_header_updated = False
			elif (not line.split(' ')[0] == "#"): #not comment
				fields = line.strip('\n').split(trace.field_delimiter, 13)
				if (len(fields) < 14): #sometimes there's no hop at all.
					continue
				if (not is_header_updated):
					src_ip = fields[1]
					header = trace.update_src_ip(header,src_ip)
					is_header_updated = True
					print header

				dst_ip = fields[2]
				timestamp = fields[5]
				replied = fields[6] #if replied, add dst_ip to hops.
				dst_rtt = fields[7] 
				hops_field = fields[13] 
				hops = build_hops(hops_field,replied,dst_ip,dst_rtt)
				
				print trace.build_trace_str(dst_ip, timestamp, hops)
		except EOFError:
			break
		except Exception, e:
			sys.stderr.write(str(e)+"\n")
			exit()
		
	sys.stderr.write("Finished parsing caida.\n")

#uniform lg.
def build_lg_hops(trace_list):
	hops=""
	for h in trace_list:
		if (h=="q"):
			hops += trace.build_hop_str([])+trace.hop_delimiter
			continue
		hops += trace.build_hop_str([(h,"*","*")])+trace.hop_delimiter
	return hops.strip(trace.hop_delimiter)

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

def uniform_lg():
	sys.stderr.write("started parsing lg ...\n")
	trace_list = []
	target_ip = ""
	while True:
		try:
			line=raw_input()
			is_delimiter = False
			if re.findall("from", line):
				target_ip = line.split(' ')[2]
				is_delimiter = True
			elif re.findall("-", line):
				continue
			else:
				hop_field=line.strip('\n').split(':')[1]
				if (re.findall("\*",hop_field)):#empty hop
					trace_list.append("q")
					continue
				if (not is_ip_ligit(hop_field)):#invalid ip
					continue
				trace_list.append(hop_field)
			
			if is_delimiter and len(trace_list) != 0:#ignore 0 len traceroute
				hops = build_lg_hops(trace_list)
				print trace.build_trace_str(target_ip, "*", hops)
				trace_list=[]

		except EOFError:
			if len(trace_list) != 0:
				hops = build_lg_hops(trace_list)
				print trace.build_trace_str(target_ip, "*", hops)
			sys.stderr.write("finished parsing lg.\n")
			break
		except Exception, e:
			sys.stderr.write("%s\n"%(e))
			break

def usage():
	sys.stderr.write("./uniform.py <source>\n")

def main(argv):
	if (len(argv) < 2):
		usage()
		exit()
	source = argv[1]
	if source == "caida":
		uniform_caida()
	elif source == "iplane":
		build_iplane()
	elif source == "lg":
		uniform_lg()

if __name__ == "__main__":
	main(sys.argv)
