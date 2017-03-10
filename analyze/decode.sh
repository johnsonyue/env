#! /bin/bash
if [ $# -ne 3 ]; then
	echo "./decode.sh <source> <data_dir> <dates>" >&2
	exit
fi

source=$1
data_dir=$2
dates=$3 #can parse more than one date


#decoding function for each source.
decode_caida_file(){
	url=$1
	echo "Message: gzip -cd $url | sc_analysis_dump" >&2
	gzip -cd $url | sc_analysis_dump #decompress and dump to stdout
}

decode_caida(){
	date_list=($dates)
	for d in $( echo ${date_list[*]} ); do
		date_dir=$data_dir"/"$d
		[ ! -d $date_dir ] && continue #skip non-existen date_dir 
		for fn in $( ls $date_dir | awk '!(NR%3)' ); do #temporary compromise
			monitor=$( echo $fn | cut -d'.' -f3 )

			#print header.
			#note that src_ip is not determined until uniform process.
			python -c "import trace; trace.print_header(\""$source"\",\""$date"\",\""$monitor"\",\"*\")"

			url=$date_dir"/"$fn
			[ -z $( echo $date_dir/$fn | grep "\.gz$" ) ] && continue #skip none-.gz file.
			decode_caida_file $url
		done
	done
}

if [ $source = "caida" ]; then
	decode_caida
elif [ $source = "iplane" ]; then
	dump_iplane
fi
