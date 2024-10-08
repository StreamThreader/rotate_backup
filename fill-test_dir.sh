#!/usr/local/bin/bash

TARGETDIR="/home/sthreader/dev/rotate_backup/test_dir"

if [ ! -d "$TARGETDIR" ]; then
    echo "directory: $TARGETDIR not found, exit"
    exit 1
fi

cd "$TARGETDIR"

# clear test_dir
#for file in $(ls 1 "$TARGETDIR/"); do
#    rm "$TARGETDIR/$file"
#done

# fill test_dir
for year in 2024; do
    for month in $(seq -w 01 12); do
	for day in $(seq -w 01 30); do
	    touch "$TARGETDIR/$year-$month-$day-v8.3-TW-ERP--01-00-d.dt"
	done
    done
done
