#!/bin/bash

if [ $# -ne 1 ]; then
        echo "./scan.sh <data_dir>" >&2
        exit
fi

data_dir=$1

for dir in $(ls $data_dir); do
        if [ ! -z $(echo $dir | grep -P "^\d{8}$") ]; then
                [ ! $(ls -1A $data_dir/$dir | wc -l) -eq 0 ] && echo $dir
        fi
done
