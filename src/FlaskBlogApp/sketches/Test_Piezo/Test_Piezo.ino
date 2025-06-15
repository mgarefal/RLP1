int piezoPin = 6; // define the digital pin that the piezo is connected to

void setup() {
  // nothing needed here
}

void loop() {
  tone(piezoPin, 440); // play a 440 Hz tone on the piezo
  delay(500); // wait for 500 milliseconds
  noTone(piezoPin); // stop the tone
  delay(500); // wait for 500 milliseconds
}