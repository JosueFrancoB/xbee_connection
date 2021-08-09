from models.devices import RemoteDevice
from digi.xbee.devices import XBeeDevice, RemoteXBeeDevice, XBee64BitAddress
import threading

def validate_open_device(device):
    try:
        if not device.is_open():
            device.open()
    except:
        print("Please restart your RaspBerry for apply app configurations")

def send_frame_xbee(device, remote_device, data):
    print(data.data.decode('utf8'))
    if data != None:
        device.send_data(remote_device, 'simon')


def receive_frame_xbee(device, remote_device):
    while True:
        data = None
        while data == None:
            data = device.read_data_from(remote_device, 15000)
        send_frame_xbee(device, remote_device, data)
    # device.close()
        

def send_to_redis():
    print('')
def receive_from_redis():
    send_frame_xbee()





# hilo1.start()