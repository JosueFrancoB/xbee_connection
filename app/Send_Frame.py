from digi.xbee.devices import XBeeDevice, RemoteXBeeDevice, XBee64BitAddress

# class SF:
#     def __init__(self):
device = XBeeDevice("/dev/ttyS0", 9600)
if not device.is_open():
    device.open()
remote_device = RemoteXBeeDevice(device, XBee64BitAddress.from_hex_string("0013A20040BA105F"))

# def SendFrame(self, data):
data = 'Holaa'
if data != None:
    device.send_data(remote_device, data)
    device.close()

