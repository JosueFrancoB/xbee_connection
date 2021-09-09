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
                    #rel_btn = os.getenv('BUTTON')
                    in_value = decode[5]
                    in_value = int(in_value) + 1
                    #if not rel_btn: rel_btn = 'big1'
                    data = requests.get(f'http://{host}:5000/in/in{str(in_value)}')
                    if data.status_code == 200:
                        resp = data.json()
                        # n_elements = len(resp)
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
                                    requests.post(f'http://{host}:5000/relevator/{pin}/{new_action}/{time}')
                                else:
                                    requests.post(f'http://{host}:5000/relevator/{pin}/{new_action}')
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
                if len(message) > 9 and not message.startswith('reg') and not message.startswith('host'):
                    data = message.split(',')
                    message, id = data[0], data[1]
                    msg = 'None'
                    #rel = os.getenv('RELEVATOR')
                    rel='A3'
                    if message == 'False':
                        requests.post(f'http://{host}:5000/relevator/{rel}/0')
                        requests.post(f'http://{host}:5000/ap/deactivate/{id}')
                        msg = 'not permission'
                    if message == 'True':
                        relevators = {'A3': '01', 'A2': '02', 'A1': '03', 'A0': '04'}
                        if rel in relevators:
                            msg = '{02'+relevators[rel]+'01}'
                            #try:
                            send_frame_xbee(device,remote,msg)
                            sleep(3)
                            requests.post(f'http://{host}:5000/ap/deactivate/{id}')
                            #except:
                            #  print('error transmit xbees')
                elif message == 'Scan':
                    device.send_data_broadcast("{04}")
                elif message.startswith('reg'):
                    data = message.split('-')
                    if data[1] == 'rel':
                        os.environ['RELEVATOR'] = data[2]
                elif message.startswith('{02'):
                    action = message[-3:]
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
                    device.send_data_broadcast('not device registered, please scan')
            else:
                print('xbee container must be start first')
