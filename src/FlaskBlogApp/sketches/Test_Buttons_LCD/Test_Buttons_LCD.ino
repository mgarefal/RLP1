#include <Wire.h>
#include <LiquidCrystal_I2C.h>
LiquidCrystal_I2C lcd(0x27, 16, 2);
const int buttonPinRED = 8;// The pin where the button is connected
const int buttonPinYELLOW = 7;
int buttonREDState = 0;     // Variable to store the button state
int buttonYELLOWState = 0;     // Variable to store the button state

void setup() {
  // Initialize the LCD
  lcd.init();
  // Turn on the backlight
  lcd.backlight();  
  pinMode(buttonPinRED, INPUT); // Set the button pin as input
  pinMode(buttonPinYELLOW, INPUT); // Set the button pin as input
  }
// Function to display text on the LCD display
void displayText(String line1, String line2) {
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print(line1);
  lcd.setCursor(0, 1);
  lcd.print(line2);
}

void loop() {
  buttonREDState = digitalRead(buttonPinRED); // Read the button state
  buttonYELLOWState = digitalRead(buttonPinYELLOW); // Read the button state
  if (buttonREDState == HIGH && buttonYELLOWState == HIGH ) { // Check if the button is pressed
    displayText("RED : Pressed", "Yellow : Pressed");
  } 
  if (buttonREDState == LOW && buttonYELLOWState == LOW ) { // Check if the button is pressed
    displayText("RED : NOT Pressed", "Yellow : NOT Pressed");
  }
  if (buttonREDState == LOW && buttonYELLOWState == HIGH ) { // Check if the button is pressed
    displayText("RED : NOT Pressed", "Yellow : Pressed");
  }
  if (buttonREDState == HIGH && buttonYELLOWState == LOW ) { // Check if the button is pressed
    displayText("RED: Pressed", "YELLOW: NOT Pressed");
  }
    delay(500); // Add a small delay to avoid flooding the serial monitor
}