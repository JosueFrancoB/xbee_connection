from digi.xbee.devices import XBeeDevice, RemoteXBeeDevice, XBee64BitAddress
from gpiozero.pins.native import NativeFactory
from gpiozero import LED
import gpiozero
import os
from time import sleep
os.system('cp /app/files_to_host/cmdline.txt /app/config_host')
os.system('cp /app/files_to_host/config.txt /app/config_host')
# class RF:
    # def __init__(self):
device = XBeeDevice("/dev/ttyS0", 9600)
factory = NativeFactory()
relay_pin = 16
relay = gpiozero.OutputDevice(relay_pin, active_high=True, initial_value=False, pin_factory=factory)
led1 = LED(22,pin_factory=factory)
led2 = LED(27,pin_factory=factory)
led3 = LED(17,pin_factory=factory)
try:
    if not device.is_open():
        device.open()
except:
    print("Please restart your RaspBerry for apply app configurations")

remote_device = RemoteXBeeDevice(device, XBee64BitAddress.from_hex_string("0013A20040BA105F"))

data = None

while data == None:
    data = device.read_data_from(remote_device, 15000)
print(data.data.decode('utf8'))
led1.on()
led2.on()
led3.on()
relay.on()
sleep(1)
print(relay.value)
relay.off()
print(relay.value)

device.close()
