Initial preprocessing functions.

1) Option 1:
Bash script to convert the log files to csv format files (from data collected by read_gyro_shorts)
Done via grep

2) Option 2:
Convert data from byte string bash to numbers (shorts or floats) if collected by another logger (like a phone BLE logger)
This uses complied code in C called from a bash file.

Both need to match the data format that was collected (shorts or floats)
