import redis
from digi.xbee.devices import XBeeDevice, RemoteXBeeDevice, XBee64BitAddress
from gpiozero.pins.native import NativeFactory
from gpiozero import LED
import gpiozero
import re
import os
import requests
from time import sleep

factory = NativeFactory()

#led1 = LED(22,pin_factory=factory)
#led2 = LED(27,pin_factory=factory)
#led3 = LED(17,pin_factory=factory)
relay_pin = 16
relay = gpiozero.OutputDevice(relay_pin, active_high=True, initial_value=False, pin_factory=factory)

#host = ''

def validate_open_device(device):
    try:
        if not device.is_open():
            device.open()
    except:
        print("Please restart your RaspBerry to apply app configurations")


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
            host = os.getenv('HOST')
            if host and host != '':
                if decode == "{0401}":
                    requests.get(f'http://{host}:5000/xbees/show/{remote}/4I4O')
                if decode.startswith('{01'):
                    msg = decode
                    msg= msg[3:-1]
                    send_to_redis(msg)
                if decode.startswith('{020'):
                    in_value = decode[5]
                    in_value = int(in_value) + 1
                    data = requests.get(f'http://{host}:5000/in/in{str(in_value)}')
                    if data.status_code == 200:
                        resp = data.json()
                        for obj in resp['routine']:
                            pin = obj['pin']
                            action = obj['action']
                            if not pin.__contains__('A'):
                                led = ''
                                led = LED(int(pin),pin_factory=factory)
                                if action == '00':
                                    led.off()
                                elif action == '01':
                                    led.on()
                            else:
                                if action.startswith('02'):
                                    new_action = action[0:2]
                                    time = action[2::]
                                    activate = '{02'+pin+new_action+time+'}'
                                    requests.post(f'http://{host}:5000/relevator/{pin}/{new_action}/{time}')
                                else:
                                    activate = '{02'+pin+action+'}'
                                    send_frame_xbee(device, remote, activate)
                                    requests.post(f'http://{host}:5000/relevator/{pin}/{action}')
            else:
                print('The xbee container must be initialized first')

def send_to_redis(data):
    publisher = redis.Redis(host = 'redis', port = 6379)
    message = data
    channel = "control"
    publisher.publish(channel, message)

def receive_from_redis(device):
    try:
        subscriber = redis.Redis(host = 'redis', port = 6379)
        channel = "test"
        p = subscriber.pubsub()
        p.subscribe(channel)
    except redis.exceptions.ConnectionError:
        print("\n Error al conectarse a redis \n")
        return
    host = ''
    while True:
        message = p.get_message()
        if message and not message['data']==1:
            message = message['data'].decode('utf-8')
            if message.startswith('host'):
                ip_host = message.split(':')
                host = ip_host[1]
                os.environ['HOST'] = ip_host[1]
            if host and host != '':
                if len(message) > 12 and not message.startswith('host'):
                    data = message.split(',')
                    message, id, key = data[0], data[1], data [2]
                    if message == 'False':
                        # requests.post(f'http://{host}:5000/relevator/{rel}/0')
                        requests.post(f'http://{host}:5000/ap/deactivate/{id}')
                    if message == 'True':
                        data = requests.get(f'http://{host}:5000/rfid_device/routine/{key}')
                        if data.status_code == 200:
                            resp = data.json()
                            for obj in resp['routine']:
                                pin = obj['pin']
                                action = obj['action']
                                if not pin.__contains__('A'):
                                    led = ''
                                    led = LED(int(pin),pin_factory=factory)
                                    if action == '00':
                                        led.off()
                                    elif action == '01':
                                        led.on()
                                else:
                                    relevators = {'A3': '01', 'A2': '02','A1': '03','A0': '04'}
                                    if pin in relevators:
                                        pin = relevators[pin]
                                        if action.startswith('02'):
                                            new_action = action[0:2]
                                            time = action[2::]
                                            activate = '{02'+pin+new_action+time+'}'
                                            send_frame_xbee(device, remote, activate)
                                            requests.post(f'http://{host}:5000/ap/deactivate/{id}')
                                        else:
                                            activate = '{02'+pin+action+'}'
                                            send_frame_xbee(device, remote, activate)
                                            requests.post(f'http://{host}:5000/ap/deactivate/{id}')
                elif message == 'Scan':
                    device.send_data_broadcast("{04}")
                elif message.startswith('{02'):
                    if message[5:7] != '02':
                        action = message[-3:]
                        if action == '01}':
                            send_frame_xbee(device, remote, message)
                        elif action == '00}':
                            send_frame_xbee(device, remote, message)
                    else:
                        send_frame_xbee(device, remote, message)
                else:
                    device.send_data_broadcast('not device registered, please scan')
            else:
                print('xbee container must be start first')
