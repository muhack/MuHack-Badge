# MuHack-Badge
Official repository for MuHack Badge.

The board features an RP2040 as main microcontroller running micropython.
Its job is to setup and stream data from the Bosh Sensor Hub BHI106B, as well as controlling the LEDs.

```Hardware/``` folder contains the KiCad project

```Software/``` folder contains the BOSS system and the sketch for the ESP32

TODOs:
 - [x] Connect the interrupt line of BHI to the RP2040
 - [x] Invert TX/RX of UART between ESP32 and RP2040
 - [x] Change to a bigger footprint of ESP32 debug port
 - [x] Maybe add two button for boot sel and reset for the ESP32
 - [x] ~~Change~~ Remove button battery
 - [x] Improve silkscreen text size
 - [x] Add silkscreen label for many things (pinout, battery polarity, etc)
 - [x] Expose BHI's internal I2C and interrupt line (for future sensors)
 - [x] Move I2C pull-up resistor
 - [x] Add leds and diods polarity
 - [x] Remove power inductor (or change to an available one)
 - [ ] ~~Maybe add a way to switch LEDs data line to the ESP32 instead of the RP2040~~
 - [ ] Docs and code comments
 - [x] Remove the D16 Schottky Diode from the battery line
 - [ ] ~~Maybe add some more cap to prevent brown-out when disconnecting USB power~~
 - [ ] Add a method within BHY library to stop every sensor
 - [x] Add NFC subsystem
 - [x] Add USB connector for the ESP32
  
 Special Thanks to:
 @gcammisa and Paolino
