#include <Wire.h>
#include <LiquidCrystal_I2C.h>

int potPin = A2; // define the analog pin that the potentiometer is connected to
int potValue = 0; // variable to store the value read from the potentiometer
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
  potValue = analogRead(potPin); // read the value from the potentiometer
  displayText("Value",String(potValue));
  delay(3000); // small delay to stabilize the reading
}