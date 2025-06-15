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

  // Write text to the LCD
  lcd.setCursor(0, 0); // Set the cursor position to the top-left corner (column 0, row 0)
  lcd.print("Hello, World!");

  // (Optional) Write text to the second row
  lcd.setCursor(0, 1); // Set the cursor position to the second row (column 0, row 1)
  lcd.print("I2C with Arduino");
}

void loop() {
  // There's no need to repeat any code in this example, so the loop is empty.
}