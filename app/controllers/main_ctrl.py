from models.devices import RemoteDevice
from digi.xbee.devices import XBeeDevice, RemoteXBeeDevice, XBee64BitAddress
import redis
from gpiozero.pins.native import NativeFactory
from gpiozero import LED
import gpiozero
import os
from time import sleep
factory = NativeFactory()

led1 = LED(22,pin_factory=factory)
led2 = LED(27,pin_factory=factory)
led3 = LED(17,pin_factory=factory)
relay_pin = 16
relay = gpiozero.OutputDevice(relay_pin, active_high=True, initial_value=False, pin_factory=factory)

def validate_open_device(device):
    try:
        if not device.is_open():
            device.open()
    except:
        print("Please restart your RaspBerry for apply app configurations")


def send_frame_xbee(device, remote_device, data):
    data = str(data.data.decode('utf8'))
    if data != None:
        device.send_data(remote_device, data)


def receive_frame_xbee(device, remote_device):
    while True:
        data = None
        data = device.read_data_from(remote_device)
        if data != None:
            print(data)
            led3.on()
            print("Reciving frame in xbee")
            send_to_redis(data)

def send_to_redis(data):
    publisher = redis.Redis(host = 'redis', port = 6379)
    message= data.data.decode('utf8')
    channel = "control"
    send_message = message
    publisher.publish(channel, send_message)
    led2.on()
    print("Send msg to redis -xbee")


def receive_from_redis(device, remote_device):
    subscriber = redis.Redis(host = 'redis', port = 6379)
    channel = "test"
    p = subscriber.pubsub()
    p.subscribe(channel)


    while True:
        message = p.get_message()
        if message != None:
            print("Recieving redis response in xbee"+ str(message))
            led1.on()
            relay.on()
            sleep(3)
            led3.off()
            led2.off()
            led1.off()
            relay.off()
            #send_frame_xbee(device, remote_device, message)

