int relayPins[] = {10, 11}; // define an array with the digital pins that the relays are connected to

void setup() {
  for (int i = 0; i < 2; i++) {
    pinMode(relayPins[i], OUTPUT); // set the digital pins as output pins
  }
}

void loop() {
  for (int i = 0; i < 2; i++) {
    digitalWrite(relayPins[i], HIGH); // turn on each relay in sequence
    delay(5000); // wait for 1 second
  }
  for (int i = 0; i < 2; i++) {
    digitalWrite(relayPins[i], LOW); // turn off each relay in sequence
    delay(5000); // wait for 1 second
  }
}