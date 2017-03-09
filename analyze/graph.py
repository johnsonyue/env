import sys
import bz2
import time

import trace

def build_graph():
        node=[]
        node_dict={}
        edge={}
        tm = time.time()
        cnt = 0
        while True:
                try:
                        prev_node = -1
                        line = raw_input()
                        if ( line.split(trace.header_delimiter)[0] == trace.header_indicator ):
                                t = time.time()
                                sys.stderr.write( "%s,%s,%s\n" % (line, t, t-tm) )
                                tm = t
                                continue

                        if ( cnt <= 499 ):
                                cnt += 1
                                continue

                        field_list = line.split(trace.field_delimiter)
                        #dst_ip = field_list[ trace.trace_index["dst_ip"] ]
                        #timestamp = field_list[ trace.trace_index["timestamp"] ]
                        hops = field_list[ trace.trace_index["hops"] ]
                        hop_list = hops.split(trace.hop_delimiter)
                        for h in hop_list:
                                if h == trace.blank_holder:
                                        continue #ignores blank
                                reply_list = h.split(trace.reply_delimiter)
                                first_reply = reply_list[0]
                                ip = first_reply.split(trace.ip_delimiter)[trace.hop_index["ip"]]
                                if (not node_dict.has_key(ip)):
                                        index = len(node)
                                        node.append(ip)
                                        node_dict[ip] = index
                                else:
                                        index = node_dict[ip]

                                if (prev_node != -1):
                                        edge[(prev_node, index)] = ""
                                prev_node = index
                except:
                        sys.stderr.write("OUTPUT\n")
                        printg(node,edge)

                        break

def printg(node, edge):
        print "%s %s" % ( len(node), len(edge.keys()) )
        for n in node:
                print n
        for e in edge.keys():
                print "%s %s" % ( str(e[0]), str(e[1]) )

if __name__ == "__main__":
        build_graph()
