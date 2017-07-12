data_dir=/ftp/raw_data/probing/
year_month=201706
out_dir=/ftp/integration/$year_month
node_out_file_name=$year_month.ip_nodes
link_out_file_name=$year_month.ip_links

[ ! -d $out_dir ] && echo "mkdir -p $out_dir" && mkdir -p $out_dir

cwd=$(pwd)
cd $data_dir
./decode.sh caida $data_dir "$(ls | grep "^year_month.*")" | python uniform.py caida | python herpes_new.py $out_dir
cd $cwd
