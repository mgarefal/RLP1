// Pin definition for the onboard LED of ESP12
const int ledPin = 2;  // GPIO2 is typically used for the onboard LED on ESP12

// Timing variables
unsigned long previousMillis = 0;  // Stores the last time the sequence ran
const long interval = 3000;        // Total interval time (3 seconds)
bool isBlinking = false;           // State control for blinking sequence
int blinkCount = 0;                // Number of blinks done
unsigned long blinkTimer = 0;      // Timer for blink timing

void setup() {
  pinMode(ledPin, OUTPUT); // Set the LED pin as an output
  digitalWrite(ledPin, HIGH); // Ensure the LED starts off (ESP12 onboard LED is active LOW)
}

void loop() {
  unsigned long currentMillis = millis();

  // Check if 3 seconds have passed
  if (!isBlinking && currentMillis - previousMillis >= interval) {
    previousMillis = currentMillis; // Update the last sequence time
    isBlinking = true;              // Start the blinking sequence
    blinkCount = 0;                 // Reset blink count
    blinkTimer = currentMillis;     // Start blink timing
  }

  // Handle blinking sequence
  if (isBlinking) {
    if (blinkCount < 4) { // 4 changes = 2 blinks (ON/OFF twice)
      if (currentMillis - blinkTimer >= 200) { // 200ms interval for each ON/OFF
        digitalWrite(ledPin, !digitalRead(ledPin)); // Toggle LED state
        blinkTimer = currentMillis;                // Reset blink timer
        blinkCount++;                              // Increment blink count
      }
    } else {
      // After 2 blinks, turn off LED and stop the sequence
      digitalWrite(ledPin, HIGH); // Ensure LED is OFF (active LOW)
      isBlinking = false;         // End blinking sequence
    }
  }
}
