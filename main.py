from time import sleep

import usb
import can

import can
import re

bus = can.interface.Bus(interface='socketcan', channel='can0', bitrate=500000)


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
    # i = int(byte, 16)
    i =byte 
    return i * 0.75 - 24


def get_rear_brake_lever(bytes):
    #D6 Byte
    byte = bytes[7]
    # Mask the last 4 bits using bitwise AND with 0xF (binary 1111)
    # last_4_bits = byte & 0xF
    first_4_bits = byte >> 4
    return first_4_bits == 3


def get_wonder_wheel_mvt(bytes):
    #D3 Byte
    byte = bytes[4]
    if byte == 0xFE:
        return "In"
    elif byte == 0xFD:
        return "Out"
    else:
        return "---"


def get_wonder_wheel(bytes):
    #D5 Byte
    byte = bytes[6]
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


for msg in bus:
    data = msg.data
    canID = msg.arbitration_id
    match canID:
        #Engine Temp
        case 0x2bc:
            eng_temp = get_engine_temp(data)
            print(f"Temperatura Água: {eng_temp}")
            #Brake lever and turn signals -> Check if it's true with realtime data
        case 0x130:
            rear_brake = get_rear_brake_lever(data)
            print(f"Travão Traseiro: {rear_brake}")
            #WonderWheel:
        case 0x2a0:
            wonder_wheel_mvt = get_wonder_wheel_mvt(data)
            wonder_wheel = get_wonder_wheel(data)  #-> This is shady need to investigate
            print(f"Wonder: {wonder_wheel_mvt} -> rotations: {wonder_wheel}")
            #Driving Mode
        case 0x2b4:
            driving_mode = get_driving_mode(data)
            print(f"Driving Mode: {driving_mode}")
    # print(msg.data)
