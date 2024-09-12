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


def get_brake_lever(bytes):
    #D0 Byte
    byte = bytes[0]
    match byte:
        case 0x81:
            return "OFF"
        case 0xa1:
            return "ON"


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


def get_rpm(bytes):
    #D3 
    byte = bytes[3]
    #Low nibble thousands
    thousands = byte & 0x0f
    #High nibble 16ths
    theeths = byte >> 4
    return f"{theeths}{thousands}"


def get_throttle_pos(bytes):
    #D5 byte
    return round((bytes[5] / 255) * 100)


def get_menu_btn(bytes):
    #D2 byte
    match bytes[2]:
        case 0x00:
            return "inactive"
        case 0x20:
            return "up"
        case 0x10:
            return "down"


def get_blinker_signal(bytes):
    print(bytes)
    #D5 low nibble
    match bytes[5]:
        case 0x41:
            return "OFF"
        case 0x42:
            return "LEFT"
        case 0x44:
            return "RIGHT"
        case 0x45:
            return "HAZARDS"


def get_fuel_to_reserve(bytes):
    #D3 byte
    return (bytes[3] / 255) * 100


def get_fuel_level(bytes):
    #D0 high nibble
    optn1 = bytes[0] >> 4
    #D1 low nibble 
    op2 = bytes[1] & 0x0F
    print(f"D0 high: {optn1}; D1 low {op2}")
    return op2


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

#region Brake

label_brake = tk.Label(frame, text="Brakes:")
label_brake.grid(row=3, column=0, padx=5, pady=5)

textbox_brake = tk.Entry(frame)
textbox_brake.grid(row=3, column=1, padx=5, pady=5)

brake_value = tk.StringVar()
textbox_brake.config(textvariable=brake_value)

#endregion

#region RPM

label_rpm = tk.Label(frame, text="RPM:")
label_rpm.grid(row=4, column=0, padx=5, pady=5)

textbox_rpm = tk.Entry(frame)
textbox_rpm.grid(row=4, column=1, padx=5, pady=5)

rpm_value = tk.StringVar()
textbox_rpm.config(textvariable=rpm_value)

#endregion

#region throttle POS

label_throttle_pos = tk.Label(frame, text="Throttle Position:")
label_throttle_pos.grid(row=5, column=0, padx=5, pady=5)

textbox_throttle_pos = tk.Entry(frame)
textbox_throttle_pos.grid(row=5, column=1, padx=5, pady=5)

throttle_pos_value = tk.StringVar()
textbox_throttle_pos.config(textvariable=throttle_pos_value)

#endregion

#region Menu Btn

label_menu_btn = tk.Label(frame, text="Menu Button:")
label_menu_btn.grid(row=6, column=0, padx=5, pady=5)

textbox_menu_btn = tk.Entry(frame)
textbox_menu_btn.grid(row=6, column=1, padx=5, pady=5)

menu_btn_value = tk.StringVar()
textbox_menu_btn.config(textvariable=menu_btn_value)

#endregion

#region wonder wheel

label_wonder_wheel = tk.Label(frame, text="Wonder Wheel:")
label_wonder_wheel.grid(row=7, column=0, padx=5, pady=5)

textbox_wonder_wheel = tk.Entry(frame)
textbox_wonder_wheel.grid(row=7, column=1, padx=5, pady=5)

wonder_wheel_value = tk.StringVar()
textbox_wonder_wheel.config(textvariable=wonder_wheel_value)

#endregion

#region blinker

label_blinker = tk.Label(frame, text="Blinker:")
label_blinker.grid(row=8, column=0, padx=5, pady=5)

textbox_blinker = tk.Entry(frame)
textbox_blinker.grid(row=8, column=1, padx=5, pady=5)

blinker_value = tk.StringVar()
textbox_blinker.config(textvariable=blinker_value)

#endregion

#region fuel level
label_fuel_level = tk.Label(frame, text="Fuel Level:")
label_fuel_level.grid(row=9, column=0, padx=5, pady=5)

textbox_fuel_level = tk.Entry(frame)
textbox_fuel_level.grid(row=9, column=1, padx=5, pady=5)

fuel_level_value = tk.StringVar()
textbox_fuel_level.config(textvariable=fuel_level_value)
#endregion

#region fuel to reserve

label_fuel_reserve = tk.Label(frame, text="Fuel to reserve:")
label_fuel_reserve.grid(row=10, column=0, padx=5, pady=5)

textbox_fuel_reserve = tk.Entry(frame)
textbox_fuel_reserve.grid(row=10, column=1, padx=5, pady=5)

fuel_reserve_value = tk.StringVar()
textbox_fuel_reserve.config(textvariable=fuel_reserve_value)

#endregion

def receive_can_data():
    last_wonder_wheel = 0
    #Connect to adapter
    bus = can.interface.Bus(interface='socketcan', channel='can0', bitrate=500000)
    for msg in bus:
        data = msg.data
        canID = msg.arbitration_id
        match canID:
            #Engine Temp -> Working
            case 0x2bc:
                water_temp_value.set(f"{get_engine_temp(data)}ºc")
                # print(f"Temperatura Água: {eng_temp}")
            #Brake -> Working
            case 0x2d2:
                brake_value.set(get_brake_lever(data))
            #WonderWheel and menu button: -> Working
            case 0x2a0:
                wonder_wheel_mvt = get_wonder_wheel_mvt(data)
                wonder_wheel = get_wonder_wheel(data)  #-> This is shady need to investigate
                if wonder_wheel > last_wonder_wheel:
                    #wheel UP
                    wonder_wheel_value.set("UP")
                elif wonder_wheel < last_wonder_wheel:
                    #wheel down
                    wonder_wheel_value.set("DOWN")
                else:
                    wonder_wheel_value.set(wonder_wheel_mvt)
                last_wonder_wheel = wonder_wheel
                menu_btn_value.set(get_menu_btn(data))
            #Driving Mode -> Working
            case 0x2b4:
                driving_mode = get_driving_mode(data)
                driving_mode_value.set(driving_mode)
                # print(f"Driving Mode: {driving_mode}")
            #Odometer -> Working
            case 0x3f8:
                odo_value.set(f"{get_odometer(data)} Km")
            #Trottle Position -> working
            case 0x110:
                throttle_pos_value.set(f"{get_throttle_pos(data)} %")
            #Blinkers and fuel level -> Not Working
            case 0x2d0:
                blinker_value.set(get_blinker_signal(data)) # Works
                fuel_level_value.set(get_fuel_level(data))
                fuel_reserve_value.set(get_fuel_to_reserve(data))

def start_can_thread():
    can_thread = threading.Thread(target=receive_can_data)
    can_thread.daemon = True  # Make sure the thread exits when the main program closes
    can_thread.start()


# Start the CAN thread when the program starts
start_can_thread()

# Run the Tkinter event loop
root.mainloop()
