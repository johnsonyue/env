import trace
import subprocess
import time
import sys
import os

from geoip import geoip

def output(team,date,monitor,line_dict,data_dir):
	for k in line_dict.keys():
		lines=line_dict[k]
		store(k,team,date,monitor,lines,data_dir)

def store(cn,team,date,monitor,lines,data_dir):
	path="%s/%s"%(data_dir,date)
	if ( not os.path.exists(path) ):
		os.makedirs(path)
	
	fn="%s/%s.%s.%s.%s.crabs.gz" % (path,team,date,monitor,cn)
	fp=open(fn,'w')
	h = subprocess.Popen(['gzip', '-c', '-'], stdin=subprocess.PIPE, stdout=fp)
	for l in lines:
		h.stdin.write(l+'\n')
	h.stdin.close()

def usage():
	print "python country.py <data_dir>"

def main(argv):
	if len(argv) < 2:
		usage()
		exit()
	
	data_dir=argv[1]

	country_list = [
		"CN","US","JP","KR","RU",
		"SY","IR","LY","AF","IQ",
		"PK","TW","HK"
	]
	geo = geoip.geoip_helper()
        tm = time.time()

	line_dict={}
	team=""
	date=""
	monitor=""
	while True:
		try:
			line=raw_input()

			#handle header line
                        if ( line.split(trace.header_delimiter)[0] == trace.header_indicator ):
				#progress info.
                                t = time.time()
                                sys.stderr.write( "%s,%s,%s\n" % (line, t, t-tm) )
                                tm = t

				#output
				if (team and date and monitor):
					output(team, date, monitor, line_dict, data_dir)
					line_dict={}
				#update team,date,monitor
				fields_list=line.split(trace.header_delimiter)[1:]
				team=fields_list[trace.header_index["team"]]
				date=fields_list[trace.header_index["date"]]
				monitor=fields_list[trace.header_index["monitor"]]
				continue

			#trace line.
                        field_list = line.split(trace.field_delimiter)
                        dst_ip = field_list[ trace.trace_index["dst_ip"] ]
			cn=geo.query(dst_ip)["bgp"]["country"]
			if cn in country_list:
				if not line_dict.has_key(cn):
					line_dict[cn]=[line]
				else:
					line_dict[cn].append(line)

		except EOFError:
			output(team,date,monitor,line_dict,data_dir)
                        break
		except Exception, e:
			print e
			break

if __name__ == "__main__":
	main(sys.argv)
