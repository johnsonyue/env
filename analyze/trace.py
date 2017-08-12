#For reference: CAIDA "warts" format
#trace = {
#	"source":0, #{caida, iplane, lg, ripeatlas ..}
#	"date":1, #{yyyymmdd}
#	"src_ip":2, #Source IP of skitter/scamper monitor performing the trace.
#	"dst_ip":3, #Destination IP being traced.
#	"timestamp":4, #Timestamp when trace began to this destination.
#	"hops":5, #Response hop list.
#	"requestttl":6, #TTL set in request packet which elicited a response from the destination.
#	"replyttl":7, #TTL found in reply packet from destination.
#	"haltreason":8, #The reason, if any, why incremental probing stopped.
#	"haltdata":9 #Extra data about why probing halted.
#}

header_index = {
	"source":0, #{caida, iplane, lg, ripeatlas ..}
	"team":1,
	"date":2, #yyyymmdd
	"true_date":3,
	"monitor":4, #name of the monitor
	"src_ip":5, #Source IP of skitter/scamper monitor performing the trace.
}
trace_index = {
	"dst_ip":0, #Destination IP being traced.
	"timestamp":1, #Timestamp when trace began to this destination.
	"hops":2 #Response hop list.
}
hop_index = {
	"ip":0, #IP address which sent a TTL expired packet.
	"rtt":1, #RTT of the TTL expired packet.
	"ntries":2 #number of tries before response received from hop.
}

#use ' ' as header delimiter.
#use '!!' as header indicator.
header_delimiter = " "
header_indicator = "!!"

field_delimiter = "\t"

hop_delimiter = " " #hop_delimiter must differ from field_delimiter
ip_delimiter = ","
reply_delimiter = ";"
blank_holder = "q"

country_seperator = "|" #seperator used in country.py output.

def print_header(source, team, date, true_date, monitor, src_ip):
	print ( "%s%s%s%s%s%s%s%s%s%s%s%s%s" % (header_indicator, header_delimiter, source, header_delimiter, team, header_delimiter, date, header_delimiter, true_date, header_delimiter, monitor, header_delimiter, src_ip) )

def bash_import():
	print "declare -A header"
	print "header=(",
	for k,v in header_index.items():
		print ( "[%s]=\"%d\" " % (k, v) ),
	print ")"

	print "declare -A trace"
	print "trace=(",
	for k,v in trace_index.items():
		print ( "[%s]=\"%d\" " % (k, v) ),
	print ")"

	return ""

def update_src_ip(header, src_ip):
	fields = header.split(header_delimiter)
	fields[header_index["src_ip"]] = src_ip
	
	header = "!!"
	for i in range(len(fields)):
		header += " "+fields[i]
	
	return header

def build_trace_str(dst_ip, timestamp, hops):
	field_list = ["" for i in range( len(trace_index.keys()) )]
	field_list[ trace_index["dst_ip"] ] = dst_ip
	field_list[ trace_index["timestamp"] ] = timestamp
	field_list[ trace_index["hops"] ] = hops
	
	str = ""
	for i in range(len(field_list)):
		str += field_list[i]+field_delimiter
	
	return str.strip(field_delimiter)

#hop: each hop could consist of up to 3 replies.
#     hop is the reply_list, 
#     each item in reply_list is a tuple, 
#     format of the tuple corresponds to hop_index
def build_hop_str(hop):
	if len(hop) == 0:
		return "q"
	
	rpl_str=""
	for i in range(len(hop)):
		ip = hop[i][hop_index["ip"]]
		rtt = hop[i][hop_index["rtt"]]
		ntries = hop[i][hop_index["ntries"]]
		rpl_str += "%s%s%s%s%s%s" % (ip, ip_delimiter, rtt, ip_delimiter, ntries, reply_delimiter)
	return rpl_str.strip(reply_delimiter)

def usage():
	#sort dict by value.
	header_items = sorted( header_index.items(), lambda a,b: cmp(a[1],b[1]) )
	trace_items = sorted( trace_index.items(), lambda a,b: cmp(a[1],b[1]) )
	print "Header: "
	for k,v in header_items:
		print ( "%d. %s" % (v, k) )
	print "Trace: "
	for k,v in trace_items:
		print ( "%d. %s" % (v, k) )
	
	print "   Hop format:"
	print "          / q                               (for no responding IP)"
	print "         |"
	print "   hop= <   IP,RTT,nTries                   (for only one responding IP)"
	print "         |"
	print "          \ IP,RTT,nTries;IP,RTT,nTries;... (for multiple responding IPs)"
	print "   where"
	print "       IP -- IP address which sent a TTL expired packet"
	print "       RTT -- RTT of the TTL expired packet"
	print "       nTries -- number of tries before response received from hop"
