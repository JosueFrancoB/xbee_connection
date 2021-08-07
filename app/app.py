import os
from digi.xbee.devices import XBeeDevice
from models.devices import RemoteDevice

os.system('cp /app/files_to_host/cmdline.txt /app/config_host')
os.system('cp /app/files_to_host/config.txt /app/config_host')

device = XBeeDevice("/dev/ttyS0", 9600)
device = RemoteDevice(device, "0013A20040BA105F")
