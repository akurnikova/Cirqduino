/*
   Read from accelerometer and write to the BLE
*/

#include <Arduino_LSM9DS1.h>
#include <ArduinoBLE.h>

//BLEPeripheral blePeripheral;
BLEService SensService("c0be9c58-a717-4e18-828c-a41836f0c7e5");
BLECharacteristic sensorval("9a067338-1da7-4e0f-8b4a-1e445e1e2df9", BLENotify, 16);

unsigned long init_time;

void setup() {
  
  pinMode(2,INPUT_PULLUP);
  pinMode(3,INPUT_PULLUP);

  //Serial.begin(9600);

  if (!IMU.begin()) {
    while (1);
  }

  // begin initialization
  if (!BLE.begin()) {
    while (1);
  }
  

  // Set a local name for the BLE device
  BLE.setLocalName("GyroAccelMonitor");
  BLE.setAdvertisedService(SensService); // add the service UUID

  SensService.addCharacteristic(sensorval);
  //AccService.addCharacteristic(Gyro);

  BLE.addService(SensService);

  init_time = millis();

  // start advertising
  BLE.advertise();
  digitalWrite(LED_BUILTIN, HIGH);
  
}


// send Accel data
void sendCombinedData() {
  short outval[8];
  float measurement[3];

  // write the button outputs 100 for accel data
  outval[0] = (short) (unsigned short) millis();
  outval[1] = (short) digitalRead(2)+2*digitalRead(3);

  IMU.readGyroscope(measurement[0], measurement[1], measurement[2]);
  outval[2] = (short) round(10*measurement[0]);
  outval[3] = (short) round(10*measurement[1]);
  outval[4] = (short) round(10*measurement[2]);

  IMU.readAcceleration(measurement[0], measurement[1], measurement[2]); 

  outval[5] = (short) round(1000*measurement[0]);
  outval[6] = (short) round(1000*measurement[1]);
  outval[7] = (short) round(1000*measurement[2]);
    
  sensorval.setValue((byte *) &outval, 16); 
}

void loop() {
  BLEDevice central = BLE.central();
  if(central)
  {
    // turn on the LED to indicate the connection:
    digitalWrite(LED_BUILTIN, LOW);
    
    while (central.connected()) {

      if (IMU.accelerationAvailable()) {
        if (IMU.gyroscopeAvailable()) {
          sendCombinedData();
        }
      }
    }
    
    digitalWrite(LED_BUILTIN, HIGH);
  }

}
