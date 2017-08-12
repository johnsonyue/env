#!/bin/bash
#test.
[ $# -ne 2 ] && echo './run.sh $action $temp_dir' && exit
action=$1
temp_dir=$2
[ "$action" == "load" ] && python trsim.py $action file sfgraph
[ "$action" == "new" ] && python trsim.py $action file sfgraph >save
./decode.sh text_file . save | python uniform.py caida | python herpes_new.py $temp_dir

cp file.nodes $temp_dir
cd $temp_dir
gzip -cd noteam.notruedate.nomonitor.herpes_node.gz >save.nodes
sort -n file.nodes>sort1
sort -n save.nodes>sort2
diff sort1 sort2
cd ../

cp file.links $temp_dir
cd $temp_dir
gzip -cd noteam.notruedate.nomonitor.herpes_link.gz >save.links
sort -n file.links>sort3
sort -n save.links>sort4
diff sort3 sort4
cd ../
