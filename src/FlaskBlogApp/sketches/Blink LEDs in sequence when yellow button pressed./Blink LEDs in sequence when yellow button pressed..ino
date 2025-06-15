const int yellowButtonPin = 8; // Yellow button connected to pin 8
const int redButtonPin = 7;    // Red button connected to pin 7
const int ledPins[] = {2, 3, 4}; // LEDs connected to pins 2, 3, and 4

bool yellowButtonState = HIGH; // Current state of the yellow button
bool blinkSequenceActive = false;

void setup() {
  pinMode(yellowButtonPin, INPUT);
  pinMode(redButtonPin, INPUT);

  // Set yellow button pin to HIGH (active state with the pull-up resistor)
  digitalWrite(yellowButtonPin, HIGH);
  
  for (int i = 0; i < 3; i++) {
    pinMode(ledPins[i], OUTPUT);
  }
}

void loop() {
  // Read the state of the yellow button
  bool newYellowButtonState = digitalRead(yellowButtonPin);

  // Check if the yellow button is pressed and released to start the blink sequence
  if (newYellowButtonState == LOW && yellowButtonState == HIGH) {
    delay(20); // Debounce delay
    newYellowButtonState = digitalRead(yellowButtonPin);
    if (newYellowButtonState == LOW) {
      blinkSequenceActive = true;
      blinkLEDs();
    }
  }
  
  // Store the current state of the yellow button
  yellowButtonState = newYellowButtonState;

  // Check if the red button is pressed and released to stop the blink sequence
  if (digitalRead(redButtonPin) == LOW) {
    delay(20); // Debounce delay
    if (digitalRead(redButtonPin) == LOW) {
      blinkSequenceActive = false;
      turnOffLEDs();
    }
  }
}

void blinkLEDs() {
  while (blinkSequenceActive) {
    for (int i = 0; i < 3; i++) {
      digitalWrite(ledPins[i], HIGH); // Turn on the current LED
      delay(1000); // 1 second delay
      digitalWrite(ledPins[i], LOW);  // Turn off the current LED
    }
  }
}

void turnOffLEDs() {
  for (int i = 0; i < 3; i++) {
    digitalWrite(ledPins[i], LOW); // Turn off all LEDs
  }
}
