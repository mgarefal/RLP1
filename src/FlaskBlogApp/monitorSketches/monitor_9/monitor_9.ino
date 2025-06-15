#include <Wire.h>

#define SLAVE_ADDRESS 8

void setup() {
  Wire.begin(SLAVE_ADDRESS);         // Initialize I2C communication as slave
  Wire.onRequest(sendData);          // Register callback function for sending data
  
  // Set all digital pins as inputs
  for (int pin = 2; pin <= 13; pin++) {
    pinMode(pin, INPUT);
  }
  
  // Set all analog pins as inputs
  for (int pin = A0; pin <= A5; pin++) {
    pinMode(pin, INPUT);
  }
}

void loop() {
  delay(100); // Add a small delay
}

void sendData() {
  byte buffer[32]; // Allocate buffer for the data
  
  int index = 0;
  
  // Read digital pin statuses
  for (int pin = 2; pin <= 13; pin++) {
    int state = digitalRead(pin);
    buffer[index++] = state; // Add pin status to buffer
  }
 
  // Read analog pin values
  for (int pin = A0; pin <= A5; pin++) {
    int value = analogRead(pin);
    buffer[index++] = highByte(value);   // Add high byte to buffer
    buffer[index++] = lowByte(value);    // Add low byte to buffer
  }
  
  // Send data over I2C only if requested
  Wire.write(buffer, sizeof(buffer)); // Send data buffer
}