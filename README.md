# Cirqduino

Project to collect and parse circus moves from DIY wearable.

**Overview**

I. Collection
* Device is made using a nano-BLE-33. Mounted on right shoulder (clavicle). Should be okay to wear for silks.
* Data (3axis axelerometer+3axis gyro+2 indicator buttons) collected via BLE connection (20B packets) interfacing with python code.
* Another option is to collect data via a log in any program as a string, then convert post-hoc.

II. Data Processing
Files are csv's with descriptive names. These are parsed in pandas/python then preprocessed and split for training a model.

III. Model goals
* Goal is to use a tensorflow lite model to extract as much information as possible
* Try other models as well to compare

Initial goals to try are
- [x] Collect the data using BLE.
- [ ] Explore options to use wifi, speed up collection.
- [x] Setup preproc pipeline
- [x] Setup to visualize data with video
- [x] Setup model testing pipeline
- [ ] Setup visuliazation for model results evaluation
- [ ] Make models to identify identify silks vs ground movements.
- [ ] Make models to identify 'salto' moves. Possibly distinguish 'drop' vs 'pike' salto. Possibly early on in the movement


Data display functions are made to combine inertial sensor data with optional video. Or to plot phase transformations of the data.
