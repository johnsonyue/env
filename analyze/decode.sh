#! /bin/bash
if [ $# -lt 3 ]; then
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
		for fn in $( ls $date_dir ); do #temporary compromise
			team=$( echo $fn | cut -d'.' -f1 )
			monitor=$( echo $fn | cut -d'.' -f3 )
			true_date=$( echo $fn | cut -d'.' -f2 )

			#print header.
			#note that src_ip is not determined until uniform process.
			python -c "import trace; trace.print_header(\""$source"\",\""$team"\",\""$d"\",\""$true_date"\",\""$monitor"\",\"*\")"

			url=$date_dir"/"$fn
			[ -z $( echo $date_dir/$fn | grep "\.gz$" ) ] && continue #skip none-.gz file.
			decode_caida_file $url
		done
	done
}

decode_crabs(){
	date_list=($dates)
	for d in $( echo ${date_list[*]} ); do
		date_dir=$data_dir"/"$d
		[ ! -d $date_dir ] && continue #skip non-existen date_dir 
		for fn in $( ls $date_dir ); do #temporary compromise
			team=$( echo $fn | cut -d'.' -f1 )
			monitor=$( echo $fn | cut -d'.' -f3 )
			true_date=$( echo $fn | cut -d'.' -f2 )

			#print header.
			#note that src_ip is not determined until uniform process.
			python -c "import trace; trace.print_header(\""$source"\",\""$team"\",\""$d"\",\""$true_date"\",\""$monitor"\",\"*\")"

			url=$date_dir"/"$fn
			[ -z $( echo $date_dir/$fn | grep "\.gz$" ) ] && continue #skip none-.gz file.
			gzip -cd $url 
		done
	done
}

decode_warts(){
	date_list=($dates)
	for d in $( echo ${date_list[*]} ); do
		date_dir=$data_dir"/"$d
		[ ! -d $date_dir ] && continue #skip non-existen date_dir 
		for fn in $( ls $date_dir ); do #temporary compromise
			team=$( echo $fn | cut -d'.' -f1 )
			monitor=$( echo $fn | cut -d'.' -f3 )
			true_date=$( echo $fn | cut -d'.' -f2 )

			#print header.
			#note that src_ip is not determined until uniform process.
			python -c "import trace; trace.print_header(\""$source"\",\""$team"\",\""$d"\",\""$true_date"\",\""$monitor"\",\"*\")"

			url=$date_dir"/"$fn
			[ -z $( echo $date_dir/$fn | grep "\.warts$" ) ] && continue #skip none-.warts file.
			sc_analysis_dump $url
		done
	done
}

decode_text(){
	date_list=($dates)
	for d in $( echo ${date_list[*]} ); do
		date_dir=$data_dir"/"$d
		[ ! -d $date_dir ] && continue #skip non-existen date_dir 
		for fn in $( ls $date_dir ); do #temporary compromise
			team=$( echo $fn | cut -d'.' -f1 )
			monitor=$( echo $fn | cut -d'.' -f3 )
			true_date=$( echo $fn | cut -d'.' -f2 )

			#print header.
			#note that src_ip is not determined until uniform process.
			python -c "import trace; trace.print_header(\""$source"\",\""$team"\",\""$d"\",\""$true_date"\",\""$monitor"\",\"*\")"

			url=$date_dir"/"$fn
			[ -z $( echo $date_dir/$fn | grep "\.text$" ) ] && continue #skip none-.warts file.
			cat $url
		done
	done
}

decode_text_file(){
	fn=$1
	team="noteam"
	monitor="nomonitor"
	true_date="notruedate"
	python -c "import trace; trace.print_header(\""$source"\",\""$team"\",\""$d"\",\""$true_date"\",\""$monitor"\",\"*\")"

	cat $fn
}

if [ $source = "caida" ]; then
	decode_caida
elif [ $source = "iplane" ]; then
	dump_iplane
elif [ $source = "crabs" ]; then
	decode_crabs
elif [ $source = "warts" ]; then
	decode_warts
elif [ $source = "text" ]; then
	decode_text
elif [ $source = "text_file" ]; then
	decode_text_file $3
fi
