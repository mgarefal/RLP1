#include <Wire.h>

const byte slaveAddress = 0x04;
unsigned long previousMillis = 0;
const long interval = 5000;  // 1 second
char dataToSend = 'A';
void setup() {
  Wire.begin(slaveAddress);
}

void loop() {
  unsigned long currentMillis = millis();
  if (currentMillis - previousMillis >= interval) {
    previousMillis = currentMillis;
    dataToSend++;
    Wire.beginTransmission(slaveAddress);
    delay(10);
    Wire.write('the x is:');
    Wire.write(dataToSend);
    Wire.endTransmission();
  }
}
