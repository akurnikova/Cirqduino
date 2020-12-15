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

  Serial.begin(9600);

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
  float outval[4];
  float dummy[2];
  unsigned long t_button;
  byte outvalbyte[16];
  byte tbyte[4];
  byte outarray[20];

  t_button = 4*millis();
  t_button = t_button + digitalRead(2);
  t_button = t_button + 2*digitalRead(3);
   
  tbyte = (byte *) &t_button
  Serial.println(tbyte, HEX)

  // write the time outputs 100 for accel data
  //for(int i=0;i<4;i++){
  //  outarray[i] = tbyte[i]
  // }
  // outarray[0] = (byte *) &(digitalRead(2)+2*digitalRead(3));

  //IMU.readGyroscope(dummy[0], outval[0], outval[1]);
  //IMU.readAcceleration(outval[2], outval[3], dummy[1]); 
  
  //outvalbyte = (byte *) &outval
  
  //for(int i=4;i<20;i++){
  //  outarray[i] = outvalbyte[i-4]
  //}
  //Serial.println(outarray)
  //sensorval.setValue(&outarray, 20); 
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
