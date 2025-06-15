const int LED_PIN = 2;
const int BUTTON_PIN = 8; // Replace 2 with the actual button pin you are using

bool ledState = LOW;       // Store the current state of the LED
bool lastButtonState = LOW; // Store the previous state of the button

void setup() {
  pinMode(LED_PIN, OUTPUT);
  pinMode(BUTTON_PIN, INPUT_PULLUP);
}

void loop() {
  // Read the current state of the button (LOW when pressed, HIGH when released)
  bool buttonState = digitalRead(BUTTON_PIN);

  // Check if the button is pressed (LOW state) and was not pressed before
  if (buttonState == LOW && lastButtonState == HIGH) {
    // Toggle the LED state
    ledState = !ledState;
    digitalWrite(LED_PIN, ledState);
  }

  // Store the current button state for the next iteration
  lastButtonState = buttonState;

  // You can add other code here if needed

  delay(20); // Small delay to avoid button bouncing
}
