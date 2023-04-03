#include <Arduino.h>
#ifndef SERIALCOMMANDER_H
#define SERIALCOMMANDER_H

// Command definitions for the serial commander
#define COMMAND_SEPARATOR "#" // TODO: fin a better way to separate commands
#define COMMAND_SET_SSID "SSID"
#define COMMAND_SET_PASSWORD "PASSWORD"
#define COMMAND_SET_HOST "HOST"
#define COMMAND_SET_PORT "PORT"
#define COMMAND_CLED "CLED"
#define COMMAND_SENSOR "SENSOR"

#define ANIM_STOP_THREAD "stopcCledThread"
#define ANIM_BLINK_ALL "blinkAll"
#define ANIM_GOES_ROUND "goesRound"
#define ANIM_DRAW_LEVEL "drawLevel"
#define ANIM_DRAW_ARROW "drawArrow"
#define ANIM_DRAW_VECTOR "drawVector"
#define ANIM_DRAW_LED "drawLed"

// Class for handle serial command

class SerialCommander{
    public:
        SerialCommander();
        void sendCommand(String command);
        void setSingleLed(int led, int r, int g, int b);
        void activateSensor(int sensor_id, int wakeup_status, int sample_rate, int max_report_latency_ms, int flush_sensor, int change_sensitivity, int dynamic_range);
        void drawVector(int x, int y, int z, int max_value);
        String readCommand();

    private:
        String ssid;
        String password;
        String host;
        int port;
       
};  // End of class SerialCommander

#endif
