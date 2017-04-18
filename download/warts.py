import time
import json
import os
import sys

from worker import request_handler

def usage():
        print "python country.py <source>"

def main(argv):
        if len(argv) < 2:
                usage()
                exit()

        data_source = argv[1]
        handler = request_handler.RequestHandler("config.json")

        config = json.loads(open("config.json").read())

        if data_source == "caida":
                root_dir = config["worker"]["root_dir"]
                out_dir = config["worker"]["out_dir"]
                if (not os.path.exists(out_dir)):
                        os.makedirs(out_dir)
                date = ""
                while(True):
                        try:
                                date = handler.get_task(data_source)
                                print date
                                sys.stdout.flush()

                                start_time = time.time()
                                print handler.notify_started(date,data_source),
                                sys.stdout.flush()

				print  "./decode.sh %s %s %s | python warts.py %s" % (data_source, root_dir, date, out_dir) 
                                os.chdir( "../analyze" ) #ugly,can't change until I figure out a better way
                                ret = os.system( "./decode.sh %s %s %s | python warts.py %s" % (data_source, root_dir, date, out_dir) )
                                os.chdir( "../download" )

                                end_time = time.time()
                                time_used = end_time - start_time
                                if (not ret):
                                        print handler.notify_finished(date, time_used, data_source),
                                        sys.stdout.flush()
                                else:
                                        print handler.notify_terminated(date,data_source)
                                        exit()

                        except KeyboardInterrupt:
                                print handler.notify_terminated(date,data_source)
                                break
                        except Exception, e:
                                print e
                                break

if __name__ == "__main__":
        main(sys.argv)
