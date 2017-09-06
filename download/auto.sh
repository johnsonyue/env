#!/bin/bash

sleep_time=$((1*60*60))

while true; do
	proc=$(ps -ef | grep "python download.py caida" | grep -v "grep")
	test ! -z "$proc" && date && echo "sleep $sleep_time" && sleep $sleep_time && continue

	date
	echo "python cron.py caida"
	python cron.py caida

	date
	echo "nohup python download.py caida >>download_log 2>&1 &"
	nohup python download.py caida >>download_log 2>&1 &
done
