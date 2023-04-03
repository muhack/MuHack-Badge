#include <Arduino.h>
#include "WebHandlers.h"
// HTML & CSS contents which display on web server
// String HTML = "<!DOCTYPE html>\
// <html>\
// <body>\
// <h1>My First Web Server with ESP32 - Station Mode &#128522;</h1>\
// </body>\
// </html>";

// void handle_root() {
//   server.send(200, "text/plain", HTML);
// }

void handle_NotFound(AsyncWebServerRequest *request){
  request->send(404, "text/plain", "Not found");
}

//void handle_ledGreen() {
//  digitalWrite(46, HIGH);
//  delay(1000);
//  digitalWrite(46, LOW);
//  server.send(200, "text/plain", "Green LED on");
//}

void handle_drawVector(AsyncWebServerRequest *request) {
  int x, y, z, max_value = 0;
  x = request->getParam("x")->value().toInt();
  y = request->getParam("y")->value().toInt();
  z = request->getParam("z")->value().toInt();
  max_value = request->getParam("max_value")->value().toInt();
  
  serialCommander.drawVector(x, y, z, max_value);
  request->send(200, "text/plain", "Drawing Vector");
}

//void handle_Sensor() {
//  int sensor_id, sample_rate, max_report_latency_ms, flush_sensor, change_sensitivity, dynamic_range = 0;
//  bool wakeup_status = false;
//  sensor_id = server.arg("sensor_id").toInt();
//  wakeup_status = server.arg("wakeup_status").toInt();
//  sample_rate = server.arg("sample_rate").toInt();
//  max_report_latency_ms = server.arg("max_report_latency_ms").toInt();
//  flush_sensor = server.arg("flush_sensor").toInt();
//  change_sensitivity = server.arg("change_sensitivity").toInt();
//  dynamic_range = server.arg("dynamic_range").toInt();
//  
//  serialCommander.activateSensor(sensor_id, wakeup_status, sample_rate, max_report_latency_ms, flush_sensor, change_sensitivity, dynamic_range);
//  server.send(200, "text/plain", "Setting Sensor");
//}
