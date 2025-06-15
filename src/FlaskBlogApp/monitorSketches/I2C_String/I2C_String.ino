#include <Wire.h>

const byte slaveAddress = 0x04;
unsigned long previousMillis = 0;
const long interval = 1000;  // 1 second
const char* textToSend = "Hello, RPi!";
byte textIndex = 0;

void setup() {
  Wire.begin(slaveAddress);
  Wire.onRequest(sendData);
}

void loop() {
  unsigned long currentMillis = millis();
  if (currentMillis - previousMillis >= interval) {
    previousMillis = currentMillis;
    textIndex++;  // Increment the index to send the next character
    if (textToSend[textIndex] == '\0') {
      textIndex = 0;  // Reset the index if the end of the string is reached
    }
  }
}

void sendData() {
  Wire.write(textToSend[textIndex]);
}

