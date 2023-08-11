# MuHack Badge BOSS firmware
# Copyright (C) 2021 MrMoDDoM
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU Affero General Public License v3.0
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.

import sys
import time
#from time import sleep_ms
from machine import I2C, Pin, PWM, UART
from buzzer_music.buzzer_music import music
import binascii
import neopixel
import _thread
import gc
import micropython
import random
import os
import math

from BHY.bhy import BHY
from NFC.nfc import NFC
from CLED.cled import CLED

BOSS_Version = "2.0"

applications = []

autostart_file = "autostart.txt"

# We need a special buffer for the interrupts
micropython.alloc_emergency_exception_buf(100)

## I2C PINs ##
SCL_PIN = 23
SDA_PIN = 22
MAIN_I2C = I2C(1, scl=Pin(SCL_PIN), sda=Pin(SDA_PIN))
BHY_I2C_ADDR = 0x28 # 40 in decimal, should also respond to 45
NFC_I2C_ADDR = 0x53 # 83dec for access to user memory, Dynamic registers or Mailbox, 0x57 (87dec) for system area

## Interrupts PINs ##
NFC_INT_PIN = 11
BHI_INT_PIN = 15

## ESP32 communication PINs ##
ESP_TX_PIN = 16
ESP_RX_PIN = 17
ESP_COM_PIN_45 = 12
ESP_COM_PIN_48 = 13
ESP_COM_PIN_47 = 14

## Frontal RGB LED PINs ##
LED_LETTER_PIN = 18
LED_LETTER_LEN = 2

LED_STRIPE_PIN = 19
LED_STRIPE_LEN = 12

## Buzzer and Buttons PINs ##
BUZZER_PIN = 29
BUTTON_A_PIN = 25
BUTTON_B_PIN = 24

CLED_THREAD = 0

button_A = machine.Pin(BUTTON_A_PIN, Pin.IN)
button_B = machine.Pin(BUTTON_B_PIN, Pin.IN)

bhy = BHY(MAIN_I2C, address=BHY_I2C_ADDR, int_pin=BHI_INT_PIN, debug=False)
nfc = NFC(MAIN_I2C, address=NFC_I2C_ADDR, int_pin=NFC_INT_PIN, debug=False)
cled = CLED(LED_STRIPE_PIN, LED_STRIPE_LEN, LED_LETTER_PIN, LED_LETTER_LEN, debug=False)

## Startup chime ##
song = '0 E3 1 0;2 E4 1 0;4 E3 1 0;6 E4 1 0;8 E3 1 0;10 E4 1 0;12 E3 1 0;14 E4 1 0;16 A3 1 0;18 A4 1 0;20 A3 1 0;22 A4 1 0;24 A3 1 0;26 A4 1 0;28 A3 1 0;30 A4 1 0;32 G#3 1 0;34 G#4 1 0;36 G#3 1 0;38 G#4 1 0;40 E3 1 0;42 E4 1 0;44 E3 1 0;46 E4 1 0;48 A3 1 0;50 A4 1 0;52 A3 1 0;54 A4 1 0;56 A3 1 0;58 B3 1 0;60 C4 1 0;62 D4 1 0;64 D3 1 0;66 D4 1 0;68 D3 1 0;70 D4 1 0;72 D3 1 0;74 D4 1 0;76 D3 1 0;78 D4 1 0;80 C3 1 0;82 C4 1 0;84 C3 1 0;86 C4 1 0;88 C3 1 0;90 C4 1 0;92 C3 1 0;94 C4 1 0;96 G2 1 0;98 G3 1 0;100 G2 1 0;102 G3 1 0;104 E3 1 0;106 E4 1 0;108 E3 1 0;110 E4 1 0;114 A4 1 0;112 A3 1 0;116 A3 1 0;118 A4 1 0;120 A3 1 0;122 A4 1 0;124 A3 1 0;0 E6 1 1;4 B5 1 1;6 C6 1 1;8 D6 1 1;10 E6 1 1;11 D6 1 1;12 C6 1 1;14 B5 1 1;0 E5 1 6;4 B4 1 6;6 C5 1 6;8 D5 1 6;10 E5 1 6;11 D5 1 6;12 C5 1 6;14 B4 1 6;16 A5 1 1;20 A5 1 1;22 C6 1 1;24 E6 1 1;28 D6 1 1;30 C6 1 1;32 B5 1 1;36 B5 1 1;36 B5 1 1;37 B5 1 1;38 C6 1 1;40 D6 1 1;44 E6 1 1;48 C6 1 1;52 A5 1 1;56 A5 1 1;20 A4 1 6;16 A4 1 6;22 C5 1 6;24 E5 1 6;28 D5 1 6;30 C5 1 6;32 B4 1 6;36 B4 1 6;37 B4 1 6;38 C5 1 6;40 D5 1 6;44 E5 1 6;48 C5 1 6;52 A4 1 6;56 A4 1 6;64 D5 1 6;64 D6 1 1;68 D6 1 1;70 F6 1 1;72 A6 1 1;76 G6 1 1;78 F6 1 1;80 E6 1 1;84 E6 1 1;86 C6 1 1;88 E6 1 1;92 D6 1 1;94 C6 1 1;96 B5 1 1;100 B5 1 1;101 B5 1 1;102 C6 1 1;104 D6 1 1;108 E6 1 1;112 C6 1 1;116 A5 1 1;120 A5 1 1;72 A5 1 6;80 E5 1 6;68 D5 1 7;70 F5 1 7;76 G5 1 7;84 E5 1 7;78 F5 1 7;86 C5 1 7;88 E5 1 6;96 B4 1 6;104 D5 1 6;112 C5 1 6;120 A4 1 6;92 D5 1 7;94 C5 1 7;100 B4 1 7;101 B4 1 7;102 C5 1 7;108 E5 1 7;116 A4 1 7'

sensor_config = []
bhy_upload_try = 3
one_shot_re_enable = [BHY.VS_TYPE_WAKEUP,
                      BHY.VS_TYPE_WAKEUP + BHY.BHY_SID_WAKEUP_OFFSET,
                      BHY.VS_TYPE_GLANCE,
                      BHY.VS_TYPE_GLANCE + BHY.BHY_SID_WAKEUP_OFFSET,
                      BHY.VS_TYPE_PICKUP,
                      BHY.VS_TYPE_PICKUP + BHY.BHY_SID_WAKEUP_OFFSET]


## Remapping Matrix ##
# This matrix is used to remap the sensor data to the correct axis

#   | X | Y | Z |
# Xs| 1 | 0 | 0 |
# Ys| 0 | -1| 0 |
# Zs| 0 | 0 | -1|

#remapping_matrix = [0,1,0,1,0,0,0,0,-1] # P5 ?
#remapping_matrix = [1,0,0,0,-1,0,0,0,-1] # P7 ?
remapping_matrix = [1,0,0,0,1,0,0,0,-1] # P? ? - obtained from experimenting with the accelerometer

def testHardware():
    led_stripe = neopixel.NeoPixel(machine.Pin(LED_STRIPE_PIN), LED_STRIPE_LEN)
    led_letter = neopixel.NeoPixel(machine.Pin(LED_LETTER_PIN), LED_LETTER_LEN)
    try:
        print("Testing LED Stripe")
        for j in range(255):
            for i in range(LED_STRIPE_LEN):
                rc_index = (i * 256 // LED_STRIPE_LEN) + j
                led_stripe[i] = cled.wheel(rc_index & 255)
            led_stripe.write()
            time.sleep_ms(10)

        led_stripe.fill( (0,0,0) )
        led_stripe.write()    

        print("Testing LED on Letters")
        for j in range(255):
            for i in range(LED_LETTER_LEN):
                rc_index = (i * 256 // LED_LETTER_LEN) + j
                led_letter[i] = cled.wheel(rc_index & 255)
            led_letter.write()
            time.sleep_ms(10)

        led_letter.fill( (0,0,0) )
        led_letter.write()

        print("Testing A and B buttons")
        while True:
            if button_A.value():
                led_letter[0] = (255,0,0)
            else:
                led_letter[0] = (0,0,0)

            if button_B.value():
                led_letter[1] = (255,0,0)
            else:
                led_letter[1] = (0,0,0)

            if not button_A.value() and not button_B.value():
                break

            led_letter.write()

        print("Testing Buzzer")
        mySong = music(song, pins=[Pin(BUZZER_PIN)], looping=False)

        while mySong.tick():
            time.sleep_ms(40)

    except KeyboardInterrupt:
        print("##Hardware test aborted!##")
        return

    finally:
        led_stripe.fill( (0,0,0) )
        led_stripe.write()
        led_letter.fill( (0,0,0) )
        led_letter.write()

        # De-init the neopixel object
        del led_letter
        del led_stripe
        gc.collect()

def initBhy():
    print("Uploading firmware to BMI160")
    if not bhy.upload_BHI160B_RAM():
        print("Uploading FAILED!")
        return False

    print("Upload completed. Starting MainTask, waiting for the BMI160 to come up...")
    # print("int_status:", bhy.int_status)
    # while not bhy.bhy_interrupt():
    bhy.startMainTask()
    while not bhy.int_status:
        bhy.startMainTask()
        print(".", end='')
        pass

    time.sleep_ms(100)

    # And then we set the remapping matrix
    setRemappingMatrix()

    time.sleep_ms(100)
    return True

def printSensorsList():
    my_list = []
    for i in range(1,33): # TODO: find a more reliable way to find how many sensor are available
        my_list.append(str(i) + ". " + bhy.sensorIdToName(i))

    for a,b in zip(my_list[::2],my_list[1::2]):
        print ('{:<40}{:<}'.format(a,b))

def printSensorsConfig():
    if not len(sensor_config):
        print("No sensor configured yet!\n")
    else:
        for i in range(len(sensor_config)):
            print("-"*20)
            s = sensor_config[i]
            print((str(i)+". "), end='')
            print("Sensor name:", bhy.sensorIdToName(s["sensor_id"]))
            print("\tWakeup:",s["wakeup_status"])
            print("\tSample rate:",s["sample_rate"])
            print("\tLatency ms:",s["max_report_latency_ms"])
            print("\tFlush FIFO:", end='')
            if s["flush_sensor"] == BHY.BHY_FIFO_FLUSH_ALL:
                print(" BHY_FIFO_FLUSH_ALL")
            else:
                print(" NONE")
            print("\tChange sensitivity:",s["change_sensitivity"])
            print("\tDynamic range:",s["dynamic_range"])
            print("-"*20)

    print('\n')

# Typical configuration is:
# Wakeup: FALSE
# Sample freq: 25 Hz
# Flush FIFO sensor: FALSE
# Max Report Latency: 0
# Change Sensitivity: 0
# Dynamic Range: 0

def addNewSensor():
    printSensorsList()
    id = int(input("Sensor ID: "))
    wake = input("Wakeup? [y/N]: ")
    sample = int(input("Sample rate [25]: ") or 25)
    latency = int(input("Max report latency [0]: ") or 0)
    flush_sensor = str(input("Flush Sensor data [-A-ll/-n-one]: ") or "A")
    change_sensitivity = int(input("Change Sensitivity [0]: ") or 0)
    dynamic_range = int(input("Dynamic Range [0]: ") or 0)

    if wake == 'y' or wake == 'Y':
        wake = True
    else:
        wake = False

    if flush_sensor == 'a' or flush_sensor == 'A':
        flush_sensor = BHY.BHY_FIFO_FLUSH_ALL
    else:
        flush_sensor = 0

    sensor_config.append({"sensor_id": id,
                          "wakeup_status": wake,
                          "sample_rate":sample,
                          "max_report_latency_ms": latency,
                          "flush_sensor": flush_sensor,
                          "change_sensitivity": change_sensitivity,
                          "dynamic_range": dynamic_range,
                          "to_remove": False})

    print("Sensor added!\n")

def removeSensor():
    printSensorsConfig()
    id = int(input("Sensor ID:"))
    if id >= len(sensor_config):
        print("Not a valid choice!")
    else:
        s = sensor_config[id]
        bhy.configVirtualSensor(s["sensor_id"], s["wakeup_status"], 0, 0, 0, 0, 0) # To disable a sensor, set sample reat at 0
        sensor_config.remove(s)
        print("Sensor Removed!\n")

def sensorsMenu():
    fin = False
    while not fin:
        print("### Sensors Menu ###")
        print("1. Print current configuration")
        print("2. Add a new sensor")
        print("3. Remove a sensor")
        print("4. Scan Physical Sensors")
        print("5. Calibrate Sensors")
        print("\n99. Return main menu")

        sel = input("\n> ")
        if sel == "1":
            printSensorsConfig()
        elif sel == "2":
            addNewSensor()
        elif sel == "3":
            removeSensor()
        elif sel == "4":
            scanPhysicalSensor()
        elif sel == "5":
            calibrationProccess()
        elif sel == "99":
            fin = True
        else:
          print("Bad selection!\n")

def scanPhysicalSensor():
    for i in range(33,96):
        data = bhy.readParameterPage(bhy.BHY_SYSTEM_PAGE, i, 16)
        if data:
            print("-"*20)
            print(binascii.hexlify(data))
            print("-"*20)

# TODO: Fix this function and add physical sensor query procedure
def discoverSelfTest():
    bhy.requestSelfTest()
    # Wait for interrupt
    while not bhy.bhy_interrupt():
        pass

    buffer = bhy.readFIFO()

    #print(binascii.hexlify(buffer))

    # print("Event type:", info,
    #     "\tEvent ID:", buffer[0],
    #     "\tData:", binascii.hexlify(buffer[:dim])
    #     )

    # events = bhy.parse_fifo(buffer, [BHY.EV_META_EVENTS, BHY.EV_WAKEUP_META_EVENTS])
    # for e in events:
    #     print(bhy.parseMetaEvent(e[2]))

def streamCalibration(vs_type):
    calibrated = False
    calibration_level = -1
    try:
        while not calibrated:
            # Wait for interrupt
            while not bhy.bhy_interrupt():
                pass

            buffer = bhy.readFIFO()

            events = bhy.parse_fifo(buffer, raw=True) # Dont pass the filters if we want to show everythings

            for e in events: # Loop every events read
                if e[0] == vs_type:
                    actual_level = bhy.parseVectorPlus(e[2])["accuracy"]
                    if actual_level > calibration_level:
                        calibration_level = actual_level
                        cled.drawLevel(actual_level, 3)
                        print("Level of calibration:", calibration_level)

            if calibration_level == 3:
                calibrated = True
                cled.blinkAll((255,255,255), 50, 2)
                print("Calibrated!")

        return True

    except KeyboardInterrupt:
        print("User Interrupt! Ending streaming!")
        return False

def setRemappingMatrix():
    print("Current Accelerometer map is:")
    print(bhy.getRemappingMatrix(BHY.VS_TYPE_ACCELEROMETER))
    bhy.setRemappingMatrix(BHY.VS_TYPE_ACCELEROMETER, remapping_matrix)
    print("New Accelerometer map is:")
    print(bhy.getRemappingMatrix(BHY.VS_TYPE_ACCELEROMETER))
    print("Current Megnetometer map is:")
    print(bhy.getRemappingMatrix(BHY.VS_TYPE_MAGNETIC_FIELD_UNCALIBRATED))
    bhy.setRemappingMatrix(BHY.VS_TYPE_MAGNETIC_FIELD_UNCALIBRATED, remapping_matrix)
    print("New Megnetometer map is:")
    print(bhy.getRemappingMatrix(BHY.VS_TYPE_MAGNETIC_FIELD_UNCALIBRATED))
    print("Current Gyroscope map is:")
    print(bhy.getRemappingMatrix(BHY.VS_TYPE_GYROSCOPE_UNCALIBRATED))
    bhy.setRemappingMatrix(BHY.VS_TYPE_GYROSCOPE_UNCALIBRATED, remapping_matrix)
    print("New Gyroscope map is:")
    print(bhy.getRemappingMatrix(BHY.VS_TYPE_GYROSCOPE_UNCALIBRATED))

def calibrationProccess():
    bhy.calibrated = False

    print("##This procedure will follow you to calibrate the BHI160B sensors##")
    print("\nFirst we set the remapping Matrix for the MuHack Badge pcb...")
    setRemappingMatrix()
    print("\nThen, starting from the gyroscope, lay the pcb on a flat surface:")

    bhy.configVirtualSensorWithConfig({"sensor_id": BHY.VS_TYPE_GYROSCOPE,
                                       "wakeup_status": False,
                                       "sample_rate": 200,
                                       "max_report_latency_ms": 0,
                                       "flush_sensor": 0,
                                       "change_sensitivity": 0,
                                       "dynamic_range": 0
                                       })

    if not streamCalibration(BHY.VS_TYPE_GYROSCOPE):
        print("\n##Calibration process ABORTED##\n")
        return False

    # Disable the Gyroscope
    bhy.configVirtualSensorWithConfig({"sensor_id": BHY.VS_TYPE_GYROSCOPE,
                                       "wakeup_status": False,
                                       "sample_rate": 0,
                                       "max_report_latency_ms": 0,
                                       "flush_sensor": 0,
                                       "change_sensitivity": 0,
                                       "dynamic_range": 0
                                       })
    print("Now the Accelerometer: rotate the board with 45° step in one direction")

    bhy.configVirtualSensorWithConfig({"sensor_id": BHY.VS_TYPE_ACCELEROMETER,
                                       "wakeup_status": False,
                                       "sample_rate": 200,
                                       "max_report_latency_ms": 0,
                                       "flush_sensor": 0,
                                       "change_sensitivity": 0,
                                       "dynamic_range": 0
                                       })
    if not streamCalibration(BHY.VS_TYPE_ACCELEROMETER):
        print("\n##Calibration process ABORTED##\n")
        return False

    # Disable the Accelerometer
    bhy.configVirtualSensorWithConfig({"sensor_id": BHY.VS_TYPE_ACCELEROMETER,
                                       "wakeup_status": False,
                                       "sample_rate": 0,
                                       "max_report_latency_ms": 0,
                                       "flush_sensor": 0,
                                       "change_sensitivity": 0,
                                       "dynamic_range": 0
                                       })

    print("And last, the Magnetometer: draw an 8-figure in mid-air with the board")
    bhy.configVirtualSensorWithConfig({"sensor_id": BHY.VS_TYPE_GEOMAGNETIC_FIELD,
                                       "wakeup_status": False,
                                       "sample_rate": 200,
                                       "max_report_latency_ms": 0,
                                       "flush_sensor": 0,
                                       "change_sensitivity": 0,
                                       "dynamic_range": 0
                                       })
    if not streamCalibration(BHY.VS_TYPE_GEOMAGNETIC_FIELD):
        print("\n##Calibration process ABORTED##\n")
        return False

    # Disable the Magnetometer
    bhy.configVirtualSensorWithConfig({"sensor_id": BHY.VS_TYPE_GEOMAGNETIC_FIELD,
                                       "wakeup_status": False,
                                       "sample_rate": 0,
                                       "max_report_latency_ms": 0,
                                       "flush_sensor": 0,
                                       "change_sensitivity": 0,
                                       "dynamic_range": 0
                                       })

    print("\n##Calibration completed!##\n")
    bhy.calibrated = True
    cled.clear()
    cled.np.write()

def idleAnimation():
    # startCLED() # We dont need CLED on idle
        # Activate orientation sensor
    sensor = {"sensor_id": BHY.VS_TYPE_PICKUP,
              "wakeup_status": True,
              "sample_rate": 200,
              "max_report_latency_ms": 0,
              "flush_sensor": 0,
              "change_sensitivity": 0,
              "dynamic_range": 0
             }
    bhy.configVirtualSensorWithConfig(sensor)

    sensor = {"sensor_id": BHY.VS_TYPE_WAKEUP,
              "wakeup_status": True,
              "sample_rate": 200,
              "max_report_latency_ms": 0,
              "flush_sensor": 0,
              "change_sensitivity": 0,
              "dynamic_range": 0
             }
    bhy.configVirtualSensorWithConfig(sensor)

    startCLED()

    j = 0

    fin = False

    try:
        while not fin:
            gc.collect()

            if (not button_A.value()):
                break

            # Wait for interrupt and progress the animation
            while not bhy.bhy_interrupt():
                for i in range(LED_STRIPE_LEN):
                    rc_index = (i * 256 // LED_STRIPE_LEN) + j
                    cled.np[i] = cled.wheel(rc_index & 255)

                for i in range(LED_LETTER_LEN):
                    rc_index = (i * 256 // LED_LETTER_LEN) + j
                    cled.np_letter[i] = cled.wheel(rc_index & 255)

                cled.np.write()
                cled.np_letter.write()
                time.sleep_ms(10)

                j += 1
                if j >= 255:
                    j = 0

            buffer = bhy.readFIFO()

            events = bhy.parse_fifo(buffer, False) # Dont pass the filters if we want to show everythings

            for e in events: # Loop every events read
                if (e[0] == BHY.VS_TYPE_PICKUP 
                    or e[0] == (BHY.VS_TYPE_PICKUP + BHY.BHY_SID_WAKEUP_OFFSET)
                    or e[0] == BHY.VS_TYPE_WAKEUP 
                    or e[0] == (BHY.VS_TYPE_WAKEUP + BHY.BHY_SID_WAKEUP_OFFSET)):
                    fin = True # We have been picked up!

    except Exception as e:
        raise e
    finally:
        stopCLED()
        # Disable orientation sensor
        sensor["sample_rate"] = 0
        bhy.configVirtualSensorWithConfig(sensor)
        cled.clear()
        cled.clearLetter()
        cled.np.write()
        cled.np_letter.write()

def accelerometer():
    # Activate orientation sensor
    sensor = {"sensor_id": BHY.VS_TYPE_LINEAR_ACCELERATION,
              "wakeup_status": False,
              "sample_rate": 25,
              "max_report_latency_ms": 0,
              "flush_sensor": 0,
              "change_sensitivity": 0,
              "dynamic_range": 0
             }
    bhy.configVirtualSensorWithConfig(sensor)

    startCLED()

    try:
        while True:
            if (not button_B.value()):
                break
            gc.collect()

            # Wait for interrupt
            while not bhy.bhy_interrupt():
                pass

            buffer = bhy.readFIFO()

            events = bhy.parse_fifo(buffer, False) # Dont pass the filters if we want to show everythings

            for e in events: # Loop every events read
                if e[0] == BHY.VS_TYPE_LINEAR_ACCELERATION or e[0] == (BHY.VS_TYPE_LINEAR_ACCELERATION + BHY.BHY_SID_WAKEUP_OFFSET):
                    cled.addAnimation(cled.ANIM_DRAW_VECTOR, [(e[2]['x'] * 16 ) / 32768, (e[2]['y'] * 16 ) / 32768, (e[2]['z'] * 16 ) / 32768, 10])
                    
    except Exception as e:
        raise e
    finally:
        stopCLED()
        # Disable orientation sensor
        sensor["sample_rate"] = 0
        bhy.configVirtualSensorWithConfig(sensor)
        
def compass():
    # Activate orientation sensor
    sensor = {"sensor_id": BHY.VS_TYPE_ORIENTATION,
              "wakeup_status": False,
              "sample_rate": 25,
              "max_report_latency_ms": 0,
              "flush_sensor": 0,
              "change_sensitivity": 0,
              "dynamic_range": 0
             }
    bhy.configVirtualSensorWithConfig(sensor)

    startCLED()

    try:
        while True:
            if (not button_B.value()):
                break
            gc.collect()

            # Wait for interrupt
            while not bhy.bhy_interrupt():
                pass

            buffer = bhy.readFIFO()

            events = bhy.parse_fifo(buffer, False) # Dont pass the filters if we want to show everythings

            for e in events: # Loop every events read
                if e[0] == BHY.VS_TYPE_ORIENTATION or e[0] == (BHY.VS_TYPE_ORIENTATION + BHY.BHY_SID_WAKEUP_OFFSET):
                    north = 360 - e[2]['x'] # Lock in place the rotation 
                    cled.addAnimation(cled.ANIM_DRAW_ARROW, north)
                    
    except Exception as e:
        raise e
    finally:
        stopCLED()
        # Disable orientation sensor
        sensor["sample_rate"] = 0
        bhy.configVirtualSensorWithConfig(sensor)

def multi_animations_show():
    import trickLED
    from trickLED import animations
    from trickLED import animations32
    from trickLED import generators

    try:
        import uasyncio as asyncio
    except ImportError:
        import asyncio

    tl = trickLED.TrickLED(machine.Pin(LED_STRIPE_PIN), LED_STRIPE_LEN)
    tl_letters = trickLED.TrickLED(machine.Pin(LED_LETTER_PIN), LED_LETTER_LEN)

    async def play(animation, n_frames, **kwargs):
        try:
            asyncio.run(animation.play(n_frames, **kwargs))
        except Exception as e:
            raise e
        finally:
            # needed to reset state otherwise the animations will get all jumbled when ended with CTRL+C
            # asyncio.new_event_loop()
            animation.leds.fill((0,0,0))
            animation.leds.write()
            # time.sleep(1)

    n_frames = 1000
    loop = asyncio.get_event_loop()
    try:
        while True:
            if (not button_B.value()):
                break
            
            print('Demonstrating animations press CTRL+C to cancel... or wait about 5 minutes.')
            # store repeat_n so we can set it back if we change it
            leds_repeat_n = tl.repeat_n
            # LitBits
            ani = animations.LitBits(tl)
            ani_letters = animations.LitBits(tl_letters)
            print('LitBits settings: default')
            loop.run_until_complete(asyncio.gather(
                play(ani, n_frames),
                play(ani_letters, n_frames)
            ))
            
            print('LitBits settings: lit_percent=50')
            loop.run_until_complete(asyncio.gather(
                play(ani, n_frames, lit_percent=50),
                play(ani_letters, n_frames, lit_percent=50)
            ))
            
            
            # NextGen
            ani = animations.NextGen(tl)
            ani_letters = animations.NextGen(tl_letters)
            print('NextGen settings: default')
            loop.run_until_complete(asyncio.gather(
                play(ani, n_frames),
                play(ani_letters, n_frames)
            ))
            print('NextGen settings: blanks=2, interval=150')
            loop.run_until_complete(asyncio.gather(
                play(ani, n_frames, blanks=2, interval=150),
                play(ani_letters, n_frames, blanks=2, interval=150)
            ))
            
            # Jitter
            ani = animations.Jitter(tl)
            ani_letters = animations.Jitter(tl_letters)
            print('Jitter settings: default')
            loop.run_until_complete(asyncio.gather(
                play(ani, n_frames),
                play(ani_letters, n_frames)
            ))
            print('Jitter settings: background=0x020212, fill_mode=FILL_MODE_SOLID')
            ani.generator = generators.random_vivid()
            ani_letters.generator = generators.random_vivid()
            loop.run_until_complete(asyncio.gather(
                play(ani, n_frames, background=0x020212, fill_mode=trickLED.FILL_MODE_SOLID),
                play(ani_letters, n_frames, background=0x020212, fill_mode=trickLED.FILL_MODE_SOLID)
            ))
            
            # SideSwipe
            ani = animations.SideSwipe(tl)
            ani_letters = animations.SideSwipe(tl_letters)
            print('SideSwipe settings: default')
            loop.run_until_complete(asyncio.gather(
                play(ani, n_frames),
                play(ani_letters, n_frames)
            ))

            # Divergent
            ani = animations.Divergent(tl)
            ani_letters = animations.Divergent(tl_letters)
            print('Divergent settings: default')
            loop.run_until_complete(asyncio.gather(
                play(ani, n_frames),
                play(ani_letters, n_frames)
            ))
            print('Divergent settings: fill_mode=FILL_MODE_MULTI')
            loop.run_until_complete(asyncio.gather(
                play(ani, n_frames, fill_mode=trickLED.FILL_MODE_MULTI),
                play(ani_letters, n_frames, fill_mode=trickLED.FILL_MODE_MULTI)
            ))

            # Convergent
            ani = animations.Convergent(tl)
            ani_letters = animations.Convergent(tl_letters)
            print('Convergent settings: default')
            loop.run_until_complete(asyncio.gather(
                play(ani, n_frames),
                play(ani_letters, n_frames)
            ))
            print('Convergent settings: fill_mode=FILL_MODE_MULTI')
            loop.run_until_complete(asyncio.gather(
                play(ani, n_frames, fill_mode=trickLED.FILL_MODE_MULTI),
                play(ani_letters, n_frames, fill_mode=trickLED.FILL_MODE_MULTI)
            ))

            # if tl.n > 60 and tl.repeat_n is None:
            #     print('Setting leds.repeat_n = 40, set it back to {} if you cancel the demo'.format(leds_repeat_n))
            #     tl.repeat_n = 40

            if 'trickLED.animations32' in sys.modules:
                # Fire
                ani = animations32.Fire(tl)
                ani_letters = animations32.Fire(tl_letters)
                print('Fire settings: default')
                loop.run_until_complete(asyncio.gather(
                    play(ani, n_frames),
                    play(ani_letters, n_frames)
                ))

                # Conjuction
                ani = animations32.Conjunction(tl)
                ani_letters = animations32.Conjunction(tl_letters)

                print('Conjuction settings: default')
                loop.run_until_complete(asyncio.gather(
                    play(ani, n_frames),
                    play(ani_letters, n_frames)
                ))
            
            if tl.repeat_n != leds_repeat_n:
                tl.repeat_n = leds_repeat_n


            del ani
            del ani_letters
            gc.collect()
            print("Demo completed! Repeating...\n")

                    
    except Exception as e:
        raise e
    finally:
        del tl
        del tl_letters
        gc.collect()
        pass # TODO: find the correct way to clean up the variables

def ball():
    time.sleep_ms(500)
    ball_velocity = 0 # rad/s
    ball_position = 0 # rad
    time_resolution = 0.1 # s

    friction = 40 # (calculated by a fair dice roll)

    acceleration_x = 0
    acceleration_y = 0
    acceleration_z = 0

    # Activate orientation sensor
    sensor = {"sensor_id": BHY.VS_TYPE_ACCELEROMETER,
              "wakeup_status": False,
              "sample_rate": 25,
              "max_report_latency_ms": 0,
              "flush_sensor": 0,
              "change_sensitivity": 0,
              "dynamic_range": 0
             }
    bhy.configVirtualSensorWithConfig(sensor)

    try:
        while True:
            start_time = time.ticks_us()
            if (not button_B.value()):
                break
            gc.collect()

            if bhy.bhy_interrupt(): # BHY has data to send us
                buffer = bhy.readFIFO()

                events = bhy.parse_fifo(buffer, False) # Dont pass the filters if we want to show everythings

                for e in events: # Loop every events read
                    if e[0] == BHY.VS_TYPE_ACCELEROMETER or e[0] == (BHY.VS_TYPE_ACCELEROMETER + BHY.BHY_SID_WAKEUP_OFFSET):
                        acceleration_x = e[2]['x']
                        acceleration_y = e[2]['y']
                        acceleration_z = e[2]['z']

            # Calculate the acceleration module (Pythagorean theorem)
            acceleration = int(math.sqrt(acceleration_x*acceleration_x + acceleration_y*acceleration_y ))


            # Calculate the angle beetwen the force vector and the ball position
            acceleration_angle = int(math.atan2(acceleration_y, acceleration_x) * 180 // math.pi) # Convert from rad to deg
            angle = abs(acceleration_angle - ball_position) # deg

            # Calculate the tangential acceleration
            tangential_acceleration = int(math.sin(math.radians(angle)) * acceleration)

            # Applay friction to slow down the ball
            if tangential_acceleration > friction:
                tangential_acceleration -= friction
            elif tangential_acceleration < -friction:
                tangential_acceleration += friction
            else:
                tangential_acceleration = 0

            time_resolution = time.ticks_diff(time.ticks_us(), start_time) / 1000000
            # Calculate the new velocity
            ball_velocity += tangential_acceleration * time_resolution 

            # Calculate the new position
            ball_position += (ball_velocity * time_resolution) + (0.5 * tangential_acceleration * time_resolution * time_resolution)

            ball_position = ball_position % 360

            # print("Ball pos: " + str(ball_position) + 
            #       "\t- Ball vel: " + str(ball_velocity) + 
            #       "\t- Tang acc: " + str(tangential_acceleration))

            #Draw the ball
            cled.drawBall(ball_position)
                    
    except Exception as e:
        raise e
    finally:
        # Disable the sensor
        sensor["sample_rate"] = 0
        bhy.configVirtualSensorWithConfig(sensor)

def streamESP():

    COMMAND_SENSOR = "SENSOR"
    COMMAND_CLED = "CLED"
    esp_uart = machine.UART(0, 115200, tx=Pin(ESP_TX_PIN), rx=Pin(ESP_RX_PIN))
    esp_uart.init(115200, bits=8, parity=None, stop=1, tx=Pin(ESP_TX_PIN), rx=Pin(ESP_RX_PIN))
        
    # For good measure, flush old data
    bhy.flushFifo() # TODO: THIS DONT WORKS AS EXPECTED

    startCLED()

    try:
        while True:
            if (not button_B.value()):
                break
            gc.collect()

            if esp_uart.any(): # ESP has data to send us
                #command = esp_uart.readline().decode("utf-8")
                command = ""
                # Read all the byte available
                while esp_uart.any():
                    command += esp_uart.readline().decode("utf-8")

                print(command)
                try:
                    if command.startswith(COMMAND_SENSOR):
                        bhy.configVirtualSensorWithConfig(eval(command[len(COMMAND_SENSOR):])) # Strip, eval and config the sensor
                    elif command.startswith(COMMAND_CLED):
                        to_split = command[len(COMMAND_CLED):] # Remove the leading command
                        to_split = to_split.split("#") # Split the two part: animation name and data for that animation
                        cled.addAnimation(to_split[0], eval(to_split[1])) # Add the animation to the queue
                except Exception as e:
                    print(e)
                    pass
                else:
                    print("Unknown command")
                    print(command)


            if bhy.bhy_interrupt(): # BHY has data to send us
                # We send to ESP all the data
                buffer = bhy.readFIFO()
                out = "DATA" + str(len(buffer)) + "#" + str(buffer)
                esp_uart.write(out)
                esp_uart.write('\n')
            
   
    except Exception as e:
        raise e
    finally:
        stopCLED()
        esp_uart.deinit()

def streamFifo():
    showAll = input("Show all event? [False] ")
    raw = input("Show raw data? [False] ")
    if raw == 'y' or raw == 'Y':
        raw = True
    else:
        raw = False

    filter = []
    for s in sensor_config:
        ret = bhy.configVirtualSensorWithConfig(s)
        filter.append(s["sensor_id"]) # Add this sensor to the filter

    # For good measure, flush old data
    bhy.flushFifo() # TODO: THIS DONT WORKS AS EXPECTED

    #startCLED()

    try:
        while True:
            gc.collect()

            # Wait for interrupt
            while not bhy.int_status:
                print("Waiting for interrupt")
                pass

            buffer = bhy.readFIFO()

            events = bhy.parse_fifo(buffer, raw) # Dont pass the filters if we want to show everythings
            if showAll:
                print(events)

            for e in events: # Loop every events read
                if e[0] in one_shot_re_enable:
                    # Search the current config and re-enable it
                    for c in sensor_config:
                        if c["sensor_id"] == e[0]:
                            ret = bhy.configVirtualSensorWithConfig(c) # Re-enable one-shot sensor # TODO: add proper check
                    # c = next((conf for conf in sensor_config if conf["sensor_id"] == e[0]))
                    # print(bhy.parseActivityRecognitionData(e[2])) # THIS IS NOT CORRECT EVEN IF THE DATA IS LISTED AS AN EVENT

                if e[0] == BHY.VS_TYPE_WAKEUP or e[0] == (BHY.VS_TYPE_WAKEUP + BHY.BHY_SID_WAKEUP_OFFSET):
                    #_thread.start_new_thread(cled.run, ("goesRound", [(0,255,0), 10]))
                    cled.addAnimation(cled.ANIM_BLINK_ALL, [(255,255,0), 50, 2])
                elif e[0] == BHY.VS_TYPE_PICKUP or e[0] == (BHY.VS_TYPE_PICKUP + BHY.BHY_SID_WAKEUP_OFFSET):
                    cled.addAnimation(cled.ANIM_GOES_ROUND, [(0,255,0), 50])
                elif e[0] == BHY.VS_TYPE_ORIENTATION or e[0] == (BHY.VS_TYPE_ORIENTATION + BHY.BHY_SID_WAKEUP_OFFSET):
                    north = 360 - e[2]['x']
                    cled.addAnimation(cled.ANIM_DRAW_ARROW, north)
                elif e[0] == BHY.VS_TYPE_GEOMAGNETIC_FIELD or e[0] == (BHY.VS_TYPE_GEOMAGNETIC_FIELD + BHY.BHY_SID_WAKEUP_OFFSET):
                    print(e[2])

    except KeyboardInterrupt:
        print("User Interrupt! Ending streaming!")
    finally:
        stopCLED()

def startCLED():
    print("Starting CLED system.. hold on")
    if cled.is_running:
        print("CLED systeam already running! Simply add animation with addAnimation function")
    else:
        _thread.start_new_thread(cled.run, ())
        cled.is_running = True # TODO: Seems like the _thread.start_new_thread return None even if the thread had been started

    time.sleep_ms(500) # Give some time to CLED to start

def stopCLED():
    print("Stopping CLED system.. hold on")
    if cled.is_running:
        cled.addAnimation(cled.ANIM_STOP_THREAD, [])
        cled.is_running = False
    else:
        print("CLED system is not running!")

    time.sleep_ms(500) # Give some time to CLED to start

def wakeup():
    pass

def isSleepRequested():
    pass

def modeSelection(max_sel):
    sel = 0
    wheel = 0
    pressed = False
    waited = 0
    while True:
        # if isSleepRequested():
        #     print("Sleep requested! Going to deepsleep...")
        #     machine.deepsleep()
        #     break

        if (not button_B.value()):
            break

        if (not button_A.value()) and (not pressed):
            pressed = True
            sel += 1
        elif button_A.value():
            pressed = False

        cled.np.fill((0,0,0))
        cled.np[sel % max_sel] = cled.wheel(wheel)
        cled.np.write()
        time.sleep_ms(50)
        wheel += 1
        wheel = wheel % 255

        if pressed: # User is choosing, need to reset the idle time
            waited = 0
        else:
            waited += 1

        if waited >= 250:
            waited = 0
            print("Starting idle Animation")
            idleAnimation()
            # print("Sleep requested! Going to deepsleep...")
            # machine.deepsleep()

    return (sel % max_sel)

def headlessMain(auto_start = None):
    time.sleep_ms(100)
    state = 0
    fin = False
    # First we try to configure the BHY
    for i in range(3):
        if not initBhy():
            print("Retring...")
        else:
            break

    # Then we install the wakeup interrupt
    # Pin.irq(handler=None, trigger=Pin.IRQ_FALLING | Pin.IRQ_RISING, *, priority=1, wake=None, hard=False)
    #machine.Pin(NFC_INT_PIN).irq(trigger=Pin.IRQ_RISING, handler=wakeup, wake=machine.DEEPSLEEP)
    #nfc_gpo = machine.Pin(NFC_INT_PIN, machine.Pin.IN)

    if auto_start is not None: # The user configured an app to be automatically started
        try:
            globals()[auto_start]()
        except:
            print("The application you configured to be automatically started is not available. Please check the configuration file")

    while not fin:
        sel = modeSelection(len(applications)) # Let the user select the application with the LED circle
        print("Starting application number", sel)
        applications[sel]() # Actually call the function
        time.sleep_ms(1000)

def NFCMenu():
    fin = False
    while not fin:
        print("### NFC Menu ###")
        print("1. Dump memory")
        print("2. Erease memory")
        print("3. Write memory")
        print("\n99. Return main menu")

        sel = input("\n> ")
        if sel == "1":
            nfc.dumpMemory()
        elif sel == "2":
            nfc.fillMemory(b'\x00')
        elif sel == "3":
            data = input("Data to write: ")
            addr = input("Address to write: ")
            nfc.writeToMemory(int(addr), data)
        elif sel == "99":
            fin = True
        else:
          print("Bad selection!\n")

def print_menu():
    print("1. Configure i2c and upload RAM patch to BHY")
    print("2. Print BHY Internal Informations")
    print("3. Hardware Test")
    print("4. Sensors Menu")
    print("5. NFC menu")
    print("\n6. Start streaming data")

    print("\n88. ESP32 UART passthrough (WIP)")
    print("\n\n99. Drop out to REPL prompt")

#uart_lock = _thread.allocate_lock()

def from_stdin_to_uart(uart, a):
    while True:
        uart.write(sys.stdin.read(1))

def UARTPassThrough():
    try:
        esp_uart = machine.UART(0, 115200, tx=Pin(ESP_TX_PIN), rx=Pin(ESP_RX_PIN))

        sys_uart_thread = _thread.start_new_thread(from_stdin_to_uart, (esp_uart,1))
        while True:
            if esp_uart.any(): # ESP has data to send us
                sys.stdout.write(esp_uart.read())
    except KeyboardInterrupt:
        print("User Interrupt! Ending UART passthrough!")

def main():
    printWelcome()
    fin = False

    gc.enable()

    #MAIN_I2C = I2C(1, sda=Pin(sda), scl=Pin(scl))

    while not fin:
        print_menu()
        sel = input("\n> ")
        if sel == "1":
            for i in range(bhy_upload_try):
                if not initBhy():
                    print("\nFailed Upload! Retring...")
                else:
                    break

        elif sel == "2":
            print(bhy.dump_Chip_status())
        elif sel == "3":
            testHardware()
        elif sel == "4":
            sensorsMenu()
        elif sel == "5":
            NFCMenu()
        elif sel == "6":
            streamFifo()
        #elif sel == "6":
        #    nfc.dumpMemory()
        elif sel == "7":
            multi_animations_show()
        elif sel == "88":
            UARTPassThrough()
        elif sel == "99":
            print("Bye Bye BOSS!")
            fin = True
        else:
            ("Bad selection!\n")

def startUpAnimation():
    startup_chime = "6 C6 1 8;0 C5 1 43;1 F5 1 8;2 A5 1 8;3 C6 1 8;5 A5 1 8"
    cled.fillFromBottom((0,255,0), 100)
    mySong = music(startup_chime, pins=[Pin(BUZZER_PIN)], looping=False)
    while mySong.tick():
        time.sleep_ms(40)

    time.sleep_ms(100)
    cled.clear()
    cled.np.write()

def printWelcome():
  welcomes = [
      '''
    ██████╗  ██████╗ ███████╗███████╗
    ██╔══██╗██╔═══██╗██╔════╝██╔════╝
    ██████╔╝██║   ██║███████╗███████╗
    ██╔══██╗██║   ██║╚════██║╚════██║
    ██████╔╝╚██████╔╝███████║███████║
    ╚═════╝  ╚═════╝ ╚══════╝╚══════╝
    ''',
      '''
    ▀█████████▄   ▄██████▄     ▄████████    ▄████████
      ███    ███ ███    ███   ███    ███   ███    ███
      ███    ███ ███    ███   ███    █▀    ███    █▀
     ▄███▄▄▄██▀  ███    ███   ███          ███
    ▀▀███▀▀▀██▄  ███    ███ ▀███████████ ▀███████████
      ███    ██▄ ███    ███          ███          ███
      ███    ███ ███    ███    ▄█    ███    ▄█    ███
    ▄█████████▀   ▀██████▀   ▄████████▀   ▄████████▀
    ''',
      '''
    ███████████     ███████     █████████   █████████
    ░░███░░░░░███  ███░░░░░███  ███░░░░░███ ███░░░░░███
    ░███    ░███ ███     ░░███░███    ░░░ ░███    ░░░
    ░██████████ ░███      ░███░░█████████ ░░█████████
    ░███░░░░░███░███      ░███ ░░░░░░░░███ ░░░░░░░░███
    ░███    ░███░░███     ███  ███    ░███ ███    ░███
    ███████████  ░░░███████░  ░░█████████ ░░█████████
    ░░░░░░░░░░░     ░░░░░░░     ░░░░░░░░░   ░░░░░░░░░
    ''',
      '''
    ▄▄▄▄·       .▄▄ · .▄▄ ·
    ▐█ ▀█▪▪     ▐█ ▀. ▐█ ▀.
    ▐█▀▀█▄ ▄█▀▄ ▄▀▀▀█▄▄▀▀▀█▄
    ██▄▪▐█▐█▌.▐▌▐█▄▪▐█▐█▄▪▐█
    ·▀▀▀▀  ▀█▄▀▪ ▀▀▀▀  ▀▀▀▀
    ''',
      '''
     ___  ___  ___ ___
    | _ )/ _ \/ __/ __|
    | _ \ (_) \__ \__ \\
    |___/\___/|___/___/
    ''',
      '''
    ███   ████▄    ▄▄▄▄▄    ▄▄▄▄▄
    █  █  █   █   █     ▀▄ █     ▀▄
    █ ▀ ▄ █   █ ▄  ▀▀▀▀▄ ▄  ▀▀▀▀▄
    █  ▄▀ ▀████  ▀▄▄▄▄▀   ▀▄▄▄▄▀
    ███
    ''',
      '''
    ▄▀▀█▄▄   ▄▀▀▀▀▄   ▄▀▀▀▀▄  ▄▀▀▀▀▄
    ▐ ▄▀   █ █      █ █ █   ▐ █ █   ▐
      █▄▄▄▀  █      █    ▀▄      ▀▄
      █   █  ▀▄    ▄▀ ▀▄   █  ▀▄   █
    ▄▀▄▄▄▀    ▀▀▀▀    █▀▀▀    █▀▀▀
    █    ▐             ▐       ▐
    ▐
    '''
  ]

  print(welcomes[random.randrange(len(welcomes) - 1)])
  print("Welcome to B.O.S.S. - Badge Operating Small System! Version: " + BOSS_Version + "\n")

if __name__ == "__main__":
    print("Starting...")
    # import lowpower
    # time.sleep_ms(1000)
    # print("before dormant")
    # btn6 = Pin(BUTTON_A_PIN, Pin.IN)
    # btn6.irq(lambda e: print("button 6 event!"), Pin.IRQ_RISING | Pin.IRQ_FALLING) 
    # lowpower.dormant_until_pin(BUTTON_A_PIN)
    # # lowpower.dormant_with_modes({
    # #     NFC_INT_PIN: (lowpower.EDGE_LOW | lowpower.EDGE_HIGH),
    # # })
    # print("after dormant") # only print after receiving signal on Pin number DORMANT_PIN

    SIE_STATUS=const(0x50110000+0x50)
    CONNECTED=const(1<<16)
    SUSPENDED=const(1<<4)
    try:
        gc.enable()
        
        # Turn off all the LEDs
        cled.clear()
        cled.np.write()
        cled.clearLetter()
        cled.np_letter.write()

        startUpAnimation()

        applications.append(compass)
        applications.append(accelerometer)
        #applications.append(streamESP)
        applications.append(multi_animations_show)
        applications.append(ball)
        #applications.append(calibrationProccess)

        if autostart_file in os.listdir(): # Check if we have an autostart file
            app = open(autostart_file).read() # Read the file
            print("Autostarting " + app) # Print the app name
            headlessMain(app)  # Start the app
        else:
            # Check if we have a serial connection active
            if (machine.mem32[SIE_STATUS] & (CONNECTED | SUSPENDED))==CONNECTED and button_B.value():
                main()
            else: # If we dont, we start the headless mode
                headlessMain()

    except KeyboardInterrupt: # TODO: can't use it on micropython?
        print("\n\nKeyboard Interrupt catched! Use menu -99- to exit\n")
    except Exception as e:
        cled.np.fill((255,0,0))
        cled.np.write()
        print("#"*10 + "ERROR" + "#"*10)
        print("Got this error while running:")
        sys.print_exception(e)
        print("#"*25)

