# start delimiter: 7E
# length: 00 0E
# frame type: 0x10
# adress_64: 0013A20040BA105F
# address16: FF FE
# receive options: C2
# Checksum: 
def frame_generator(frame_type, adress_64, address16, msg):
    frame_typei = int(frame_type, 16)
    adress_64 = int(adress_64, 16)
    address16 = int(address16, 16)
    start_delimiter = int('7E',16)
    length = int('000E', 16)
    data = [ord(c) for c in msg]
    str1 = ""
    for ele in data: 
        str1 += str(ele)  
    # print(str1)
    str1 = hex(int(str1, 16))
    print(str1.decode("hex"))
    if frame_type == '0x10':
        length += len(data)
        print((hex(start_delimiter)+hex(length)).replace('0x', ''))

frame_generator('0x10', '0013A20040BA105F', 'FFFE', 'hola')

