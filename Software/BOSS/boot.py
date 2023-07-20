# boot.py -- run on boot-up
import os

esp_prog_file = "esp-prog.txt"

# This file is executed on every boot (including wake-boot from deepsleep)
# can run arbitrary Python, but best to keep it minimal

# Check if file named esp-prog.txt exists and then delete it
# if esp_prog_file in os.listdir():
#     os.remove(esp_prog_file)    # Delete the file

#     # Now we need to start the UART pass-through between the ESP32 and the RP2040 usb serial port
#     import machine

#     # Set UART0 to 115200 baud
#     esp_uart = machine.UART(0, 115200, tx=Pin(16), rx=Pin(17))

#     while True:
#         # Read from UART0 and write to UART1
#         if uart.any():
#             uart1.write(uart.read(1))
