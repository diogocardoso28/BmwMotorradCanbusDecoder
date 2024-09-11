import re
from time import sleep
import usb.core
import usb.util
import usb.backend.libusb1

import can
#Open Log file
f = open("C:\\Users\diogo\Desktop\Motorrad Can\\bmwCANEngineON.asc", "r")

def get_message(line):
    # Regular expression to match the desired pattern
    pattern = r'(\b8(?: [A-F0-9]{2}){8}\b)'

    # Search for the pattern
    match = re.search(pattern, line)

    # Check if a match is found and extract it
    if match:
        message = match.group(1)
        return message.split(" ")


def get_engine_temp(bytes):
    #D2 Byte
    byte = bytes[3]
    i = int(byte, 16)
    return i*0.75-24

def get_rear_brake_lever(bytes):
    #D6 Byte
    byte = int(bytes[7], 16)
    # Mask the last 4 bits using bitwise AND with 0xF (binary 1111)
    # last_4_bits = byte & 0xF
    first_4_bits = byte >> 4
    return first_4_bits == 3

def get_wonder_wheel_mvt(bytes):
    #D3 Byte
    byte = int(bytes[4], 16)
    if byte == 0xFE:
        return "In"
    elif byte == 0xFD:
        return "Out"
    else:
        return "---"

def get_wonder_wheel(bytes):
    #D5 Byte
    byte = int(bytes[6], 16)
    return byte

def get_driving_mode(bytes):
    #D2 Byte
    match bytes[3]:
        case "42":
            return "Road Active"
        case "52":
            return "Road Blinking"
        case "43":
            return "Dynamic Active"
        case "5B":
            return "Dynamic Blinking"
        case "41":
            return "Rain Active"
        case "49":
            return "Rain Blinking"

for line in f.readlines():
    # Regular expression to match the desired 3-digit hexadecimal value
    pattern = r'\b([A-Fa-f0-9]{3})\b'

    # Search for the pattern
    match = re.search(pattern, line)

    # Check if a match is found and extract it
    if match:
        canID = match.group(1)
        match canID:
            #Engine Temp
            case "2bc":
                eng_temp = get_engine_temp(get_message(line))
                print(f"Temperatura Água: {eng_temp}")

            #Brake lever and turn signals -> Check if it's true with realtime data
            case "130":
                rear_brake = get_rear_brake_lever(get_message(line))
                print(f"Travão Traseiro: {rear_brake}")
            #WonderWheel:
            case "2a0":
                wonder_wheel_mvt = get_wonder_wheel_mvt(get_message(line))
                wonder_wheel = get_wonder_wheel(get_message(line)) #-> This is shady need to investigate
                print(f"Wonder: {wonder_wheel_mvt} -> rotations: {wonder_wheel}")
            #Driving Mode
            case "2b4":
                driving_mode = get_driving_mode(get_message(line))
                print(f"Driving Mode: {driving_mode}")

# backend = usb.backend.libusb1.get_backend(find_library=lambda x: "C:\\Users\\diogo\\Desktop\\libusb-1.0.dll")
#
# dev = usb.core.find(backend=backend,idVendor=0x1D50, idProduct=0x606F)
# bus =  can.Bus(interface="gs_usb", channel="candle0", index=0, bitrate=500000)