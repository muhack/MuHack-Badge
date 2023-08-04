from time import sleep_ms
from machine import I2C, Pin
import binascii
import struct

class NFC:

    def __init__(self, MAIN_I2C, address=0x53, int_pin = 0, board_version = 2, debug = False):
        self.i2c = MAIN_I2C
        self.board_version = board_version

        if int_pin:
            self.int_pin = Pin(int_pin, Pin.IN)
            self.int_pin.irq(trigger=Pin.IRQ_RISING , handler=self.nfc_int_handler)
        else:
            self.int_pin = 0

        self.NFC_ADDR = address
        self.debug = debug


    def nfc_int_handler(self, pin):
        print("--------NFC Interrupt!!!")

    def printDebug(self, msg):
        if self.debug:
            print(msg)

    def writeToMemory(self, address, data):
        self.printDebug("Writing " + str(binascii.hexlify(data)) + " to address " + str(address))
        # We need to send all the data within one transaction
        # First we send the address we want to write to, in big endian format
        out = struct.pack('>H', address)
        # Then we write add the data
        out += data
        print(out)
        # Finally we write it to the NFC chip
        self.i2c.writeto(self.NFC_ADDR, out)
        sleep_ms(10)
        self.printDebug("Data written: " + str(binascii.hexlify(data)))

    def readFromMemory(self, address, length):
        self.printDebug("Reading " + str(length) + " bytes from address " + str(address))
        # First we send the address we want to read from, in big endian format
        self.i2c.writeto(self.NFC_ADDR, struct.pack('>H', address))
        # Then we read the data
        data = self.i2c.readfrom(self.NFC_ADDR, length)
        self.printDebug("Data read: " + str(binascii.hexlify(data)))
        return data

    def dumpMemory(self):
        print("NFC Memory Dump:")
        data = ""
        for i in range(0, 256, 8):
            data += str(binascii.hexlify(self.readFromMemory(i, 8))) + "\n"
            #sleep_ms(100)
            #print("\n")
        print(data)

    def fillMemory(self, data):
        print("Filling NFC Memory with " + str(binascii.hexlify(data)))
        for i in range(0, 256, len(data)):
            self.writeToMemory(i, data)
            #sleep_ms(100)

    def clearMemory(self):
        print("Clearing NFC Memory")
        self.fillMemory(b'\x00' * 256)

