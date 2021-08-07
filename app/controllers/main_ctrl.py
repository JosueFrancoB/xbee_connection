from models.devices import RemoteDevice

def receive_frame_xbee(device, remote_device):
    data = None
    while data == None:
        data = device.read_data_from(remote_device, 15000)
    print(data.data.decode('utf8'))
    try:
        if not device.is_open():
            device.open()
    except:
        print("Please restart your RaspBerry for apply app configurations")
    device.close()

def send_frame_xbee(device, remote_device, data):
    if data != None:
        device.send_data(remote_device, data)
        device.close()

def receive_from_redis():

def send_to_redis():