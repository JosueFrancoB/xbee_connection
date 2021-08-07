from digi.xbee.devices import XBeeDevice, RemoteXBeeDevice, XBee64BitAddress
#/dev/ttyS0
#0013A20040BA105F

class RemoteDevice: 
    def __init__(self, device, adress_remote):
        self.remote_device = RemoteXBeeDevice(device, XBee64BitAddress.from_hex_string(adress_remote))