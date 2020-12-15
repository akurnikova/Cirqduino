/*
   Read from accelerometer and write to the BLE
*/

#include <Arduino_LSM9DS1.h>
#include <ArduinoBLE.h>

BLEService SensService("c0be9c58-a717-4e18-828c-a41836f0c7e5");
BLECharacteristic sensorval("9a067338-1da7-4e0f-8b4a-1e445e1e2df9", BLERead|BLENotify, 20);

float accval[5];
float gyroval[5];
int init_time;

void setup() {
  
  Serial.begin(9600);
  while (!Serial);
  Serial.println("Started");

  pinMode(2,INPUT_PULLUP);
  pinMode(3,INPUT_PULLUP);

  if (!IMU.begin()) {
    Serial.println("Failed to initialize IMU!");
    while (1);
  }
  Serial.print("Gyroscope sample rate = ");
  Serial.print(IMU.gyroscopeSampleRate());
  Serial.println(" Hz");
  Serial.println();
  Serial.println("Gyroscope in degrees/second");
  Serial.println("X\tY\tZ");

  // begin initialization
  if (!BLE.begin()) {
    Serial.println("starting BLE failed!");
    while (1);
  }
  

  // Set a local name for the BLE device
  BLE.setLocalName("GyroAccelMonitor");
  BLE.setAdvertisedService(SensService); // add the service UUID

  SensService.addCharacteristic(sensorval);
  //AccService.addCharacteristic(Gyro);

  BLE.addService(SensService);

  // start advertising
  BLE.advertise();
  digitalWrite(LED_BUILTIN, HIGH);

  init_time = millis();
  
  Serial.println("Bluetooth device active, waiting for connections...");

  
}

// send Accel data
void sendAccelData() {

   // write the button outputs 100 for accel data
  accval[4] = (float) (100+ 10*digitalRead(2)+ digitalRead(3));
  accval[3] = (float) (millis() - init_time);
  
  // read orientation x, y and z eulers
  IMU.readAcceleration(accval[0], accval[1], accval[2]); 
  
  // Send 3x accel readings over bluetooth as 1x byte array 
  sensorval.setValue((byte *) &accval, 20); 

} 

// send Gyro data
void sendGyroData() {

  // write the button outputs 200 for gyro data
  gyroval[4] = (float) (200+10*digitalRead(2) + digitalRead(3));
  gyroval[3] = (float) (millis() - init_time);
  
  // IMU.readAcceleration(gyroval[3], gyroval[4], gyroval[2]);
  IMU.readGyroscope(gyroval[0], gyroval[1], gyroval[2]);
  
  // Send 3x gyro readings over bluetooth as 1x byte array 
  sensorval.setValue((byte *) &gyroval, 20); 

} 


void loop() {
  BLEDevice central = BLE.central();
  if(central)
  {
    Serial.print("Connected to central: ");
    Serial.println(central.address());
    // turn on the LED to indicate the connection:
    digitalWrite(LED_BUILTIN, LOW);
    
    while (central.connected()) {

      if (IMU.accelerationAvailable()) {
          sendAccelData();
          sendGyroData();
      }
    }
    
    digitalWrite(LED_BUILTIN, HIGH);
    Serial.print("Disconnected from central: ");
    Serial.println(central.address());
  }

}
