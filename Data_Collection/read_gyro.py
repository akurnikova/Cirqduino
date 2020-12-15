from bluepy.btle import Scanner, DefaultDelegate, Peripheral, UUID
import struct
import itertools
import time
import sys

class ScanDelegate(DefaultDelegate):
    def __init__(self):
        DefaultDelegate.__init__(self)

    def handleNotification(self, cHandle, data):
        if cHandle == 12:
            print(time.time())
            print(struct.unpack('fffff', data))

class GAmonitor(object):

    SERVICE_UUIDS = [
        UUID('c0be9c58-a717-4e18-828c-a41836f0c7e5'), # Sensors
    ]
    
    CHARACTERISTIC_UUIDS = {
    #    '9a067338-1da7-4e0f-8b4a-1e445e1e2df8': 'ACC',
        '9a067338-1da7-4e0f-8b4a-1e445e1e2df9': 'ACC'
    }

    NOTIFICATION_CHARACTERISTIC_UUIDS = [
        'ACC',
        #'GYRO',
        ]

    # Notification data
    NOTIFICATION_ON = struct.pack("BB", 0x01, 0x00)
    NOTIFICATION_OFF = struct.pack("BB", 0x00, 0x00)

    def __init__(self, mac_address):
        self.macAddress = mac_address
        self.delegate=ScanDelegate()

    def set_delegate(self, delegate):
        self.delegate = delegate

    def connect(self):
        print('getting peripheral',sys.stderr)
        self.peripheral = Peripheral(self.macAddress, addrType='public')
        # Retrieve all characteristics from desired services and map them from their UUID
        self.peripheral.getServices()
        svc = self.peripheral.getServiceByUUID("c0be9c58-a717-4e18-828c-a41836f0c7e5")
        characteristics = {svcid: svc.getCharacteristics()[i] for svcid, i in zip(self.CHARACTERISTIC_UUIDS, range(2))}
        
        print(characteristics,sys.stderr)
        #characteristics = list(itertools.chain(*[self.peripheral.getServiceByUUID(uuid).getCharacteristics() for uuid in GAmonitor.SERVICE_UUIDS]))
        
        #characteristics = [svc.getCharacteristics()[0] for svcid in self.CHARACTERISTIC_UUIDS]
        #characteristics = dict((c.uuid, c) for c in characteristics)
        # Store each characteristic's value handle for each characteristic name
        self.characteristicValueHandles = dict((name, characteristics[uuid].getHandle()) for uuid, name in self.CHARACTERISTIC_UUIDS.items())
        
        # Subscribe for notifications
        for name in self.NOTIFICATION_CHARACTERISTIC_UUIDS:
            print('Enabling notification: ',sys.stderr)
            self.peripheral.writeCharacteristic(self.characteristicValueHandles[name]+1, self.NOTIFICATION_ON, True)
            print(name, sys.stderr)
            print(self.characteristicValueHandles[name]+1,sys.stderr)
            
        self.peripheral.setDelegate(self.delegate)

    def wait_for_notifications(self, timeout):
        self.peripheral.waitForNotifications(timeout)

if __name__ == "__main__":
    while(1):
        try: 
            GA = GAmonitor(mac_address = "fd:df:19:30:4c:91") #"f6:29:60:b4:99:4b")
            GA.connect()
            print('connected')
            while(1):
                GA.wait_for_notifications(10.0)
                print('no notification 10s')
        except Exception as e:
            print(e, sys.stderr)
            print('TRYING TO CONNECT', sys.stderr)

