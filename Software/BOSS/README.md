# Badge Operating Small System

> **NOTE: The software is still in development, so expect A LOT OF bugs and missing features.**

The calibration process is still in development: there is a small utility to calibrate the sensor, but it is currently disabled from the headless mode.

## How to use

### Serial console
Simply connect the badge to your computer and connect to the serial port with a terminal emulator (e.g. `screen` or `minicom`).

### Headless mode
Turn the badge on without any USB data connection active and select the application you want to run.

Use the button "A" to select the application and the button "B" to start/stop it.

At the moment, there are 4 applications available:
- **Compass**: a simple compass that shows the current orientation of the badge, red arrow **should** points north
- **Accelerometer**: a simple accelerometer that shows the current acceleration on the 3 axis, the led on the "h" show the outwards direction, the led on the "u" show the inwards direction
- **Light show**: a simple light show, thank to the TrickLED library (to quit, reboot the badge)
- **Ball**: simulate the presence of a ball inside the led ring, using the accelerometer

If you leave the badge idle for around 200 seconds, it will automatically start the idle animation: simply pick it up or double tap on it to return to the menu.
