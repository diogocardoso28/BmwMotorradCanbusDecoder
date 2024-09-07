import usb
import can

#Connect adapter
dev = usb.core.find(idVendor=0x1D50, idProduct=0x606F)
bus = can.Bus(
    interface="gs_usb",
    channel=dev.product,
    bus=dev.bus,
    address=dev.address,
    bitrate=250000
)

# Listen for incoming messages
with can.Bus() as bus:
    for msg in bus:
        print(msg.data)