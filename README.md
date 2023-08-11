# MuHack-Badge
Official repository for MuHack Badge.

![Badge startup](/image/startup.gif)

The board features an RP2040 as main microcontroller running micropython.
Its job is to setup and stream data from the Bosh Sensor Hub BHI106(B), as well as controlling the LEDs.

```Hardware/``` folder contains the KiCad project

```Software/``` folder contains the BOSS system and the sketches for the ESP32 (WIP)

> **NOTE: The software is still in development, so expect A LOT OF bugs and missing features.**

![Badge rotate](/image/rotate.gif)

## Chagelog v2

 - Added USB connector for the ESP32
 - Added NFC subsystem
 - Completely reworked the power system
 - Added more LEDs for battery status and esp32
 - Added a button for the ESP32
 - WIP: firmware update for better BHI support

## Chagelog v1
 - Initial release

## TODOs:
 - [x] Connect the interrupt line of BHI to the RP2040
 - [x] Invert TX/RX of UART between ESP32 and RP2040
 - [x] Change to a bigger footprint of ESP32 debug port
 - [x] Maybe add two button for boot sel and reset for the ESP32
 - [x] ~~Change~~ Remove battery switch
 - [x] Improve silkscreen text size
 - [x] Add silkscreen label for many things (pinout, battery polarity, etc)
 - [x] Expose BHI's internal I2C and interrupt line (for future sensors)
 - [x] Move I2C pull-up resistor
 - [x] Add leds and diods polarity
 - [x] Remove power inductor (or change to an available one)
 - [ ] ~~Maybe add a way to switch LEDs data line to the ESP32 instead of the RP2040~~
 - [ ] Docs and code comments
 - [x] Remove the D16 Schottky Diode from the battery line
 - [x] Maybe add some more cap to prevent brown-out when disconnecting USB power
 - [ ] Add a method within BHY library to stop every sensor
 - [x] Add NFC subsystem
 - [x] Add USB connector for the ESP32
  
 Special Thanks to:
 @gcammisa and Paolino
