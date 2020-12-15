Initial preprocessing functions.

1) Option 1:
Bash script to convert the log files to csv format files (from data collected by read_gyro_shorts)
sdjust folder names in file then run as:
bash preproc_data.sh


2) Option 2:
Convert data from byte string bash to numbers (shorts or floats) if collected by another logger (like a phone BLE logger)
This uses complied code in C called from a bash file.
run as 
sh preproc_log.sh filename_to_convert

Both need to match the data format that was collected (shorts or floats)
