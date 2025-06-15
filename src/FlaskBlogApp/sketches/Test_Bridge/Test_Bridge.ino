int enbPin = 9;  // PWM pin for speed control
int in4Pin = 12;  // Input 4 pin
int inPin = 13;   // Input pin

void setup() {
  pinMode(enbPin, OUTPUT);
  pinMode(in4Pin, OUTPUT);
  pinMode(inPin, OUTPUT);
}

void loop() {
  // Set the speed and direction of the motor
  analogWrite(enbPin, 200);  // Set the speed (0-255)
  digitalWrite(in4Pin, HIGH);  // Set the direction (HIGH for forward, LOW for backward)
  digitalWrite(inPin, LOW);

  // Wait for a few seconds
  delay(5000);

  // Stop the motor
  analogWrite(enbPin, 0);
  digitalWrite(in4Pin, LOW);
  digitalWrite(inPin, LOW);

  // Wait for a few seconds
  delay(5000);
}