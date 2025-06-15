const int photoresistorPin = A0; // The pin where the photoresistor is connected
int photoresistorValue = 0;      // Variable to store the photoresistor value
#include <Wire.h>
#include <LiquidCrystal_I2C.h>

// Set the I2C address of the module (usually 0x27 or 0x3F)
// Adjust the parameters if needed (address, columns, rows)
LiquidCrystal_I2C lcd(0x27, 16, 2);

void setup() {
 // Initialize the LCD
  lcd.init();

  // Turn on the backlight
  lcd.backlight();

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
  photoresistorValue = analogRead(photoresistorPin); // Read the photoresistor value
  displayText("Value",String(photoresistorValue));
  delay(2000); // Wait for 1 second before reading the value again
}