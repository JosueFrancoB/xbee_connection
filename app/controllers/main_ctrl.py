from models.devices import RemoteDevice
from digi.xbee.devices import XBeeDevice, RemoteXBeeDevice, XBee64BitAddress
import redis 

def validate_open_device(device):
    try:
        if not device.is_open():
            device.open()
    except:
        print("Please restart your RaspBerry for apply app configurations")


def send_frame_xbee(device, remote_device, data):
    data = str(data.data.decode('utf8'))
    print(data)
    if data != None:
        device.send_data(remote_device, data)


def receive_frame_xbee(device, remote_device):
    while True:
        data = None
        while data == None:
            data = device.read_data_from(remote_device)
        
        send_to_redis(data)
        # print(data.data.decode('utf8'))
    # device.close()


def send_to_redis(data):
    publisher = redis.Redis(host = 'localhost', port = 6379)
    message= data.data.decode('utf8')
    channel = "test"
    while message!="exit":
        # message = input("")
        send_message = "Python : " + message
        publisher.publish(channel, send_message)


def receive_from_redis(device, remote_device):
    subscriber = redis.Redis(host = 'localhost', port = 6379)
    channel = 'test'
    p = subscriber.pubsub()
    p.subscribe(channel)
    while True:
        message = p.get_message()
        if message and not message['data'] == 1:
            message = message['data'].decode('utf-8')
            send_frame_xbee(device, remote_device, message)
