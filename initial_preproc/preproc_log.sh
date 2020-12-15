#!/bin/bash
filename=$1
fle_out=$(basename $filename .txt)_preproc.csv
echo $fle_out

cat $filename | grep '\"(0x)' |sed 's/received//' | sed 's/A\t//' | sed 's/"(0x) //' | sed 's/" //'> temp_proc.txt

echo "timestamp,x,y,z,t,status" > $fle_out

while read line; do
echo $line | ./convert_vals >> $fle_out
done < temp_proc.txt

rm temp_proc.txt
#cat $filename | grep '\"(0x)' |sed 's/received//' | sed 's/A\t//' | sed 's/"(0x) //' | sed 's/" //'
