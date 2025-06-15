void setup() {
  Serial.begin(9600); // Initialize serial communication at 9600 baud rate
  randomSeed(analogRead(0)); // Seed the random number generator with an analog read
}

void loop() {
  int randomData = random(0, 100); // Generate a random number between 0 and 99
  Serial.println(randomData); // Send the random number to the serial monitor
  delay(2000); // Wait for 2 seconds
}