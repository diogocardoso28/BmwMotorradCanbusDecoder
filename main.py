# Command to enable interface
# sudo ip link set can0 up type can bitrate 500000

import threading
import can
import re
import tkinter as tk


def get_engine_temp(bytes):
    #D2 Byte
    byte = bytes[2]
    return byte * 0.75 - 25


def get_rear_brake_lever(bytes):
    #D6 Byte
    byte = bytes[6]
    # Mask the last 4 bits using bitwise AND with 0xF (binary 1111)
    # last_4_bits = byte & 0xF
    first_4_bits = byte >> 4
    return first_4_bits == 3


def get_wonder_wheel_mvt(bytes):
    #D3 Byte
    byte = bytes[3]
    if byte == 0xFE:
        return "In"
    elif byte == 0xFD:
        return "Out"
    else:
        return "---"


def get_wonder_wheel(bytes):
    #D5 Byte
    byte = bytes[5]
    return byte


def get_driving_mode(bytes):
    #D2 Byte
    match bytes[2]:
        case 0x42:
            return "Road Active"
        case 0x52:
            return "Road Blinking"
        case 0x43:
            return "Dynamic Active"
        case 0x5B:
            return "Dynamic Blinking"
        case 0x41:
            return "Rain Active"
        case 0x49:
            return "Rain Blinking"


def get_odometer(bytes):
    #DEC(D3,D2,D1)
    return (bytes[3] << 16) | (bytes[2] << 8) | bytes[1]


# Create the main window
root = tk.Tk()
root.title("Motorrad Info")

# Create a frame to hold the textboxes
frame = tk.Frame(root)
frame.pack(padx=10, pady=10)

#region Odometer

label_odo = tk.Label(frame, text="Odometer:")
label_odo.grid(row=0, column=0, padx=5, pady=5)

textbox_odo = tk.Entry(frame)
textbox_odo.grid(row=0, column=1, padx=5, pady=5)

odo_value = tk.StringVar()
textbox_odo.config(textvariable=odo_value)
#endregion

#region Water Temperature

label_water_temp = tk.Label(frame, text="Water Temperature:")
label_water_temp.grid(row=1, column=0, padx=5, pady=5)

textbox_water_temp = tk.Entry(frame)
textbox_water_temp.grid(row=1, column=1, padx=5, pady=5)

water_temp_value = tk.StringVar()
textbox_water_temp.config(textvariable=water_temp_value)


#endregion

#region Driving Mode

label_driving_mode = tk.Label(frame, text="Driving Mode")
label_driving_mode.grid(row=2, column=0, padx=5, pady=5)

textbox_driving_mode = tk.Entry(frame)
textbox_driving_mode.grid(row=2, column=1, padx=5, pady=5)

driving_mode_value = tk.StringVar()
textbox_driving_mode.config(textvariable=driving_mode_value)

#endregion

#region Rear Brake

label_rear_brake = tk.Label(frame, text="Rear Brake:")
label_rear_brake.grid(row=3, column=0, padx=5, pady=5)

textbox_rear_brake = tk.Entry(frame)
textbox_rear_brake.grid(row=3, column=1, padx=5, pady=5)

rear_brake_value = tk.StringVar()
textbox_rear_brake.config(textvariable=rear_brake_value)

#endregion


def receive_can_data():
    #Connect to adapter
    bus = can.interface.Bus(interface='socketcan', channel='can0', bitrate=500000)
    for msg in bus:
        data = msg.data
        canID = msg.arbitration_id
        match canID:
            #Engine Temp
            case 0x2bc:
                water_temp_value.set(f"{get_engine_temp(data)}ºc")
                # print(f"Temperatura Água: {eng_temp}")
            #Brake lever and turn signals -> Check if it's true with realtime data
            case 0x130:
                rear_brake = get_rear_brake_lever(data)
                rear_brake_value.set(f"{'ON' if rear_brake is True else 'OFF'}")
                # print(f"Travão Traseiro: {rear_brake}")
            #WonderWheel:
            case 0x2a0:
                wonder_wheel_mvt = get_wonder_wheel_mvt(data)
                wonder_wheel = get_wonder_wheel(data)  #-> This is shady need to investigate
                # print(f"Wonder: {wonder_wheel_mvt} -> rotations: {wonder_wheel}")
            #Driving Mode
            case 0x2b4:
                driving_mode = get_driving_mode(data)
                driving_mode_value.set(driving_mode)
                # print(f"Driving Mode: {driving_mode}")
            #Odometer
            case 0x3f8:
                print(data)
                odo_value.set(f"{get_odometer(data)} Km")


def start_can_thread():
    can_thread = threading.Thread(target=receive_can_data)
    can_thread.daemon = True  # Make sure the thread exits when the main program closes
    can_thread.start()


# Start the CAN thread when the program starts
# start_can_thread()

# Run the Tkinter event loop
root.mainloop()
