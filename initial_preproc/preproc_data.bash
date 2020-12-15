#!/bin/bash
export cirq='/home/asya/Documents/tensorflow/tensorflow/lite/micro/examples/cirque_movement/'
for input_dir in silks ctrl testdata
do
  output_dir=${input_dir}_preproc
  header='rec_time,t,button,gx,gy,gz,ax,ay,az'
  
  flelist=$(find ./$input_dir/ -name '*.txt'| grep -v readme)
  echo $filelist
  for fle in $flelist
  do
    fle_base=$(basename $fle .txt)
    
    echo $header > ./$output_dir/${fle_base}_preproc.txt
    echo ${fle_base}
    
    cat $fle | grep -v 'Note' | grep -v 'True' | grep -v 'no notification' | grep -v 'calling' | grep -v 'init' | grep -v 'name' | grep -v 'connected' | sed 's/(//' | sed s/')//' | paste - - -d ', ' >> ./$output_dir/${fle_base}_preproc.txt
  done
  cp -r $output_dir $cirq/

echo $cirq #final output directory
done
