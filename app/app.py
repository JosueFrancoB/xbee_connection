import os
import threading
from digi.xbee.devices import XBeeDevice, RemoteXBeeDevice, XBee64BitAddress
from controllers.main_ctrl import *

# Configurations in RaspBerry with ubuntu
# os.system('cp /app/files_to_host/cmdline.txt /app/config_host')
# os.system('cp /app/files_to_host/config.txt /app/config_host')

device = XBeeDevice("/dev/ttyS0", 9600)
#remote1 = RemoteXBeeDevice(device, XBee64BitAddress.from_hex_string("0013A20040BA105F"))

validate_open_device(device)
# device.send_data(remote1, 'spamm')
xbee_thread = threading.Thread(target=receive_frame_xbee, args=(device,))
redis_thread = threading.Thread(target=receive_from_redis, args=(device,))

if __name__ == '__main__':
    print("Xbee Receiver starting")    
    xbee_thread.start()
    redis_thread.start()
    xbee_thread.join()
    redis_thread.join()




