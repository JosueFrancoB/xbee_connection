from digi.xbee.devices import XBeeDevice, RemoteXBeeDevice, XBee64BitAddress
import redis
from gpiozero.pins.native import NativeFactory
from gpiozero import LED
import gpiozero
import os
import requests
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
    rmt_device = RemoteXBeeDevice(device, XBee64BitAddress.from_hex_string(remote_device))
    if data != None:
        device.send_data(rmt_device, data)


def receive_frame_xbee(device):
    while True:
        data = None
        data = device.read_data()
        if data != None:
            decode = data.data.decode('utf8')
            global remote
            remote = str(data.remote_device)
            remote = remote[0:16]
            if decode == "{0401}":
                requests.get(f'http://172.19.0.4:5000/xbees/show/{remote}/4I4O')
            if decode.startswith('{01'):
                msg = decode
                msg= msg[3:-1]
                print(msg)
                led3.on()
                print("Reciving frame in xbee")
                send_to_redis(msg)



def send_to_redis(data):
    publisher = redis.Redis(host = 'redis', port = 6379)
    message = data
    channel = "control"
    publisher.publish(channel, message)
    led2.on()
    print("Send msg to redis -xbee")


def receive_from_redis(device):
    subscriber = redis.Redis(host = 'redis', port = 6379)
    channel = "test"
    p = subscriber.pubsub()
    p.subscribe(channel)
    while True:
        message = p.get_message()
        if message and not message['data']==1:
            message = message['data'].decode('utf-8')
            if len(message) > 9 and not message.startswith('rel') and not message.startswith('action'):
                data = message.split(',')
                message, id = data[0], data[1]
                msg = 'None'
                rel = os.getenv('RELEVATOR')
                if not rel: rel='big1'
                if message == 'False':
                    requests.post(f'http://localhost:5000/relevator/{rel}/0')
                    requests.post(f'http://localhost:5000/ap/deactivate/{id}')
                    msg ='not permission'
                if message == 'True':
                    relevators = {'small1': '01', 'small2': '02', 'big1': '03', 'big2': '04'}
                    if rel in relevators:
                        msg = '{02'+relevators[rel]+'01}'
                        try:
                            send_frame_xbee(device,remote,msg)
                            sleep(3)
                            requests.post(f'http://localhost:5000/ap/deactivate/{id}')
                        except:
                            print('error transmit xbees')
            elif message == 'Scan':
                device.send_data_broadcast("{04}")
            elif message.startswith('rel'):
                data = message.split('-')
                os.environ['RELEVATOR'] = data[1]
            elif message.startswith('action'):
                relevator = message.split('-')
                code = relevator[1]
                action = code[-3:]
                if action == '01}':
                    try:
                        send_frame_xbee(device, remote, message)
                    except:
                        print('not remote device identified')
                elif action == '00}':
                    try:
                        send_frame_xbee(device, remote, message)
                    except:
                        print('not remote device identified')
            else:
                #todo: cambiar este mensaje por un protocolo para encender algun led del arduino
                device.send_data_broadcast('not device registered, please scan')
                #todo reiniciar arduino depues de scanear
