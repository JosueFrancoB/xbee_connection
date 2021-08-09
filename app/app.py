import os
import threading
from digi.xbee.devices import XBeeDevice, RemoteXBeeDevice, XBee64BitAddress
from controllers.main_ctrl import *

# os.system('cp /app/files_to_host/cmdline.txt /app/config_host')
# os.system('cp /app/files_to_host/config.txt /app/config_host')

device = XBeeDevice("COM3", 9600)
remote = RemoteXBeeDevice(device, XBee64BitAddress.from_hex_string("0013A20040BA105F"))

validate_open_device(device)

while True:
    threading.Thread(target=receive_frame_xbee, args=(device, remote)).start()

# send_frame_xbee(device, remote, "Hola")
