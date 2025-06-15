#include <Wire.h>
unsigned long startTime = 0;
String report="None";

void setup() {
  pinMode(LED_BUILTIN, OUTPUT); // Initialize the onboard LED pin as an output
  Wire.begin(8);                // Join I2C bus with address #8
  Wire.onRequest(sendReport);   // Register callback function for sending report
  startTime = millis();         // Record the start time
}

void loop() {
  unsigned long currentTime = millis();
  if (currentTime - startTime >= 120000) { // 2 minutes = 120000 milliseconds
    // After 2 minutes, turn the onboard LED on
    digitalWrite(LED_BUILTIN, HIGH);
    // Set the report to "SUCCESS"
    report="SUCCESS";
  } else {
    // Before 2 minutes, turn the onboard LED off
    digitalWrite(LED_BUILTIN, LOW);
    // Set the report to "FAILURE"
    report="FAILURE";
  }

}

void sendReport(String report) {
  // Send the report via I2C
  Wire.write(report);
}
