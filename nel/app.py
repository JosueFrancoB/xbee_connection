from digi.xbee.devices import XBeeDevice, RemoteXBeeDevice, XBee64BitAddress
from RF import RF

rf = RF
device = XBeeDevice("COM3", 9600)
if not device.is_open():
    device.open()
# device.send_data_broadcast("Si sirve")

#  remote_device = xbee_network.discover_device("REMOTE")
#         if remote_device is None:
#             print("Could not find the remote local_xbee")

#         print("Sending explicit data to %s >> %s..." % (remote_device.get_64bit_addr()))

remote_device = RemoteXBeeDevice(device, XBee64BitAddress.from_hex_string("0013A20040BA105F"))

print(remote_device.get_64bit_addr())
print(remote_device.get_16bit_addr())

# device.send_data(remote_device, "Si!")

# print(device.get_protocol())
data = None
# while data == None:
    # data = device.read_data_from(remote_device, 15000)
    # print(remote_device.get_firmware_version())
    # print(remote_device.get_hardware_version())
    # print(remote_device.get_role())
    # print('remote', remote_device.get_pan_id())

    # print('dev', device.get_firmware_version())
    # print('dev', device.get_hardware_version())
    # print('dev', device.get_role())
    # print('dev', device.get_pan_id())
print(data.remote_device)
print(data.is_broadcast)
# print(data.source_endpoint)
# print(data.dest_endpoint)
# print(data.cluster_id)
print(data.timestamp)
# data = data.data.decode('utf8')
print(data)
device.close()

