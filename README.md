# Cirqduino

Project to collect and parse circus moves from DIY wearable.

**Overview**

Device is made using a nano-BLE-33. Mounted on right shoulder (clavicle). Should be okay to wear for silks.\n
Data (3axis axelerometer+3axis gyro+2 indicator buttons) collected via BLE connection (20B packets) interfacing with python code.\n
Another option is to collect data via a log in any program as a string, then convert post-hoc.


Files are csv's with descriptive names. These are parsed in pandas/python then preprocessed and split for training a model.\n
Goal is to use a tensorflow lite model to extract as much information as possible


Initial goals to try are
--Identify 'salto' moves. Possibly distinguish 'drop' vs 'pike' salto.\n
--Identify silks vs ground.\n


Data display functions are made to combine inertial sensor data with optional video. Or to plot phase transformations of the data.
