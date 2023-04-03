#include "SerialCommander.h"

// Init SerialCommander
SerialCommander::SerialCommander(){
    ssid = "";
    password = "";
    host = "";
    port = 0;
}

// Method to send serial command to RP2040
void SerialCommander::sendCommand(String command){
    Serial.println(command);
}

// Method to set RGB LED on RP2040
void SerialCommander::setSingleLed(int led, int r, int g, int b){
    String command = String(COMMAND_CLED) + String(ANIM_DRAW_LED) + String(COMMAND_SEPARATOR) + String(led) + String(COMMAND_SEPARATOR) + String(r) + String(COMMAND_SEPARATOR) + String(g) + String(COMMAND_SEPARATOR) + String(b);
    sendCommand(command);
}

// Method to activate a sensor on the RP2040
void SerialCommander::activateSensor(int sensor_id, int wakeup_status, int sample_rate, int max_report_latency_ms, int flush_sensor, int change_sensitivity, int dynamic_range){
    String command = COMMAND_SENSOR;
    command.concat("{");
    command.concat("\"sensor_id\":");
    command.concat(sensor_id);
    command.concat(",");
    command.concat("\"wakeup_status\":");
    command.concat(wakeup_status);
    command.concat(",");
    command.concat("\"sample_rate\":");
    command.concat(sample_rate);
    command.concat(",");
    command.concat("\"max_report_latency_ms\":");
    command.concat(max_report_latency_ms);
    command.concat(",");
    command.concat("\"flush_sensor\":");
    command.concat(flush_sensor);
    command.concat(",");
    command.concat("\"change_sensitivity\":");
    command.concat(change_sensitivity);
    command.concat(",");
    command.concat("\"dynamic_range\":");
    command.concat(dynamic_range);
    command.concat("}");
    
    sendCommand(command);
}

// Method to draw a vector on the RP2040
void SerialCommander::drawVector(int x, int y, int z, int max_value){
    String command = String(COMMAND_CLED);
    command.concat(ANIM_DRAW_VECTOR);
    command.concat(COMMAND_SEPARATOR);
    command.concat("[");
    command.concat(String(x));
    command.concat(",");
    command.concat(String(y));
    command.concat(",");
    command.concat(String(z));
    command.concat(",");
    command.concat(String(max_value));
    command.concat("]");;
    sendCommand(command);
}

// Method to read serial command from RP2040
String SerialCommander::readCommand(){
    String command = "";
    while (Serial.available() > 0) {
        command += (char)Serial.read();
    }
    return command;
}
