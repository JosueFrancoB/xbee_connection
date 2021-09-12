from controllers.main_ctrl import send_frame_xbee
import requests
from gpiozero.pins.native import NativeFactory
from gpiozero import LED

factory = NativeFactory()

def execute_redis_message(message, host, device, remote):
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


def execute_xbee_message(decode, host, device, remote):
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
