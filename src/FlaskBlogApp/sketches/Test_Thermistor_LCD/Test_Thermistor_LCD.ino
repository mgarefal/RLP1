#include <LiquidCrystal_I2C.h>
int lm35Pin = A1; // define the analog pin that the LM35DZ sensor is connected to
float temperature; // variable to store the temperature in degrees Celsius

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
  int sensorValue = analogRead(lm35Pin); // read the value from the LM35DZ sensor
  temperature = (sensorValue * 5.0 / 1024.0) * 100.0; // convert the sensor value to degrees Celsius
  displayText("Temp:",String(temperature)+" C");
  delay(1000); // wait for 1 second before taking another reading
}