void setup() {
  Serial.begin(9600);

  // Set pin modes for all digital pins
  for (int digitalPin = 0; digitalPin < 14; digitalPin++) {
    pinMode(digitalPin, INPUT);
  }
}

void loop() {
  // Iterate over all digital pins
  for (int digitalPin = 0; digitalPin < 14; digitalPin++) {
    int digitalPinState = digitalRead(digitalPin);
    reportChange("Digital Pin", digitalPin, digitalPinState);
    delay(10); // Delay for debounce
  }

  // Iterate over all analog pins
  for (int analogPin = A0; analogPin < A6; analogPin++) {
    int analogPinValue = analogRead(analogPin);
    reportChange("Analog Pin", analogPin, analogPinValue);
    delay(10); // Delay for stabilization
  }
}

void reportChange(String pinType, int pinNumber, int pinValue) {
  // Report the pin status change to the RPI
  Serial.print("PIN Change: ");
  Serial.print(pinType);
  Serial.print(" ");
  Serial.print(pinNumber);
  Serial.print(" Value: ");
  Serial.println(pinValue);
}