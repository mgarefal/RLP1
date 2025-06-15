const int ledPin = 13;

void setup() {
  pinMode(ledPin, OUTPUT); // Set LED pin as output
}

void loop() {
  digitalWrite(ledPin, HIGH);  // Turn LED ON
  delay(3000);                // Wait for 1 minute (60,000 ms)

  digitalWrite(ledPin, LOW);   // Turn LED OFF
  delay(3000);                // Wait for 1 minute (60,000 ms)
}