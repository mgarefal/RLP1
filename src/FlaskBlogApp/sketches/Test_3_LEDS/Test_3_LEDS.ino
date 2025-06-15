// Pin numbers for the LEDs
const int ledPin1 = 2;
const int ledPin2 = 3;
const int ledPin3 = 4;

void setup() {
  // Set the LED pins as output
  pinMode(ledPin1, OUTPUT);
  pinMode(ledPin2, OUTPUT);
  pinMode(ledPin3, OUTPUT);
}

void loop() {
  // Turn on LED 1 and turn off the others
  digitalWrite(ledPin1, HIGH);
  digitalWrite(ledPin2, LOW);
  digitalWrite(ledPin3, LOW);
  delay(1000); // Wait for 1 second

  // Turn on LED 2 and turn off the others
  digitalWrite(ledPin1, LOW);
  digitalWrite(ledPin2, HIGH);
  digitalWrite(ledPin3, LOW);
  delay(1000); // Wait for 1 second

  // Turn on LED 3 and turn off the others
  digitalWrite(ledPin1, LOW);
  digitalWrite(ledPin2, LOW);
  digitalWrite(ledPin3, HIGH);
  delay(1000); // Wait for 1 second
}