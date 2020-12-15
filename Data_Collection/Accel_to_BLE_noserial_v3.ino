/*
   Read from accelerometer and write to the BLE
*/

#include <Arduino_LSM9DS1.h>
#include <ArduinoBLE.h>

//BLEPeripheral blePeripheral;
BLEService SensService("c0be9c58-a717-4e18-828c-a41836f0c7e5");
BLECharacteristic sensorval("9a067338-1da7-4e0f-8b4a-1e445e1e2df9", BLENotify, 20);

//unsigned long init_time;

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

  //init_time = millis();

  // start advertising
  BLE.advertise();
  digitalWrite(LED_BUILTIN, HIGH);
  
}


// send Accel data
void sendCombinedData() {
  float outval[5];
  float ind;
  float dummy[2];
  //byte outbyte[20];

  // write the button outputs 100 for accel data
  ind = (float) (millis()%32768ul);
  ind += 0.5*digitalRead(2)+0.25*digitalRead(3);
  outval[0] = ind;

  IMU.readGyroscope(outval[1], outval[2], dummy[0]);
  outval[1] = round(10*outval[1]);
  
  outval[2] = std::min(round(10*outval[2]), 8192.0)); // clip to 2**13
  outval[2] = std::max(round(10*outval[2]), -8192.0)); // clip to -2**13

  dummy[0] = std::min(round(10*dummy[0]), 8192.0)); // clip to 2**13
  dummy[0] = std::max(round(10*dummy[0]), -8192.0)); // clip to -2**13
  
  //Serial.print("gyro x: ");
  //Serial.print(dummy[0]);
  //Serial.print("gyro y: ");
  //Serial.print(dummy[1]);
  //Serial.print("gyro z: ");
  //Serial.print(outval[1]);
  //Serial.println(' ');

  IMU.readAcceleration(outval[3], outval[4], dummy[1]); 

  sensorval.setValue((byte *) &outval, 20); 
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
