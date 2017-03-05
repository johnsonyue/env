import sys

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
		if (replied):
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
		except Exception, e:
			break
		
	sys.stderr.write("Finished parsing caida.")

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

if __name__ == "__main__":
	main(sys.argv)
