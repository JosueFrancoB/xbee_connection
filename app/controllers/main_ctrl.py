import redis
import logging
from gpiozero import LED
from gpiozero.pins.native import NativeFactory
from digi.xbee.devices import RemoteXBeeDevice, XBee64BitAddress

factory = NativeFactory()

log = logging.getLogger('xbee')
console = logging.StreamHandler()
log.addHandler(console)
log.setLevel(logging.INFO)

def validate_open_device(device):
    try:
        if not device.is_open():
            device.open()
    except:
        print("Please restart your RaspBerry to apply app configurations")


def GetRedisConnection():
    r = None
    try:
        r = redis.Redis(host='redis', port=6379, decode_responses=True)
        # if r.ping():
            # log.info(colorize(f"Redis connection established on {redisConf['host']}", ['green']))print("hola")
    except Exception as e:
        r= None
        #log.info(colorize(f"Could not connect to redis server on {redisConf['host']}", ['orange']))
        #log.error(e)
        #print("hola")
    return r



def send_frame_xbee(device, remote_device, data):
    rmt_device = RemoteXBeeDevice(device, XBee64BitAddress.from_hex_string(remote_device))
    if data != None:
        try:
            device.send_data(rmt_device, data)
        except:
            print('Send message error')

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
                send_to_redis(f'Scaned,{remote},4I4O', 'scan_event')
            if decode.startswith('{01'):
                send_to_redis(decode, 'cards_event')
            if decode.startswith('{020'):
                send_to_redis(decode, 'inputs_event')

def send_to_redis(data,stream_name):    
    try:
        r= GetRedisConnection()
        if r:
            #stream_data = GetStreamData(event_key)
            stream =  'xbee.' + stream_name
            maxlen=  200
            if stream:
                r.xadd(stream, {"data": data}, maxlen=maxlen, approximate=True)
    except Exception as e:
        # log.error(e)
        pass

def receive_from_redis(device):
    events_to_listen = [
        'access_control.scan_event', 
        'access_control.relevator_event',
        'access_control.rasp_event']
    streams = {}
    r= GetRedisConnection()
    if r:
        for event in events_to_listen:
            lastid = r.get(event['lastid_key'])
            if not lastid:
                xrev_result = r.xrevrange(event, count=1)
                log.info(f'xrev_result: {xrev_result}')
                if len(xrev_result) > 0:
                    lastid = xrev_result[0][0]
                else:
                    lastid = '0-0'
            streams[event] = lastid
    r.close()
    while True:
        try:
            r = GetRedisConnection()
            if r:
                xread_result = r.xread(streams, None, 0)
                if not len(xread_result) == 0:
                    for stream_result in xread_result:
                        if not len(stream_result) == 0:
                            lastid_key = stream_result[0]
                            for event in stream_result[1]:
                                [event_id, event_data] = event
                                r.set(lastid_key, event_id)
                                streams[stream_result[0]] = event_id
                                analize_stream(event_data['data'],stream_result[0], device)
            else:
                time.sleep(2)
        except Exception as e:
            print(f"{e}")


def analize_stream(data, stream, device):
    if stream == 'access_control.relevator_event':
        send_frame_xbee(device, remote, data)
    if stream == 'access_control.rasp_event':
        data = data.split(',')
        action, pin = data[0], data[1]
        led = ''
        led = LED(int(pin),pin_factory=factory)
        if action == '00':
            led.off()
        elif action == '01':
            led.on()
        elif action == '02':
            time = action[2::]
            time = float(time)
            time /= 1000
            led.on_time(time)
        elif action == '03':
            led.toggle()
    if stream == 'access_control.scan_event':
        device.send_data_broadcast("{04}")
