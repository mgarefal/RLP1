void setup() {
  Serial.begin(9600);
  
  // Set digital pins as input
  for (int i = 2; i < 14; i++) {
    pinMode(i, INPUT);
  }
}

void loop() {
  if (Serial.available() > 0) {
    String receivedString = Serial.readString();
    receivedString.trim();

    if (receivedString == "report") {
      Serial.print("Pin States|");

      // Read and print digital pin states in one line
      for (int i = 2; i < 14; i++) {
        Serial.print("Pin ");
        Serial.print(i);
        Serial.print(":");
        Serial.print(digitalRead(i));
        Serial.print("|");  // Delimiter
      }

      // Read and print analog pin values in one line
      for (int i = 0; i < 6; i++) {
        Serial.print("A");
        Serial.print(i);
        Serial.print(":");
        Serial.print(analogRead(i));
        if (i < 5) Serial.print("|"); // Add delimiter except for the last value
      }

      Serial.println();  // End of line
    }
  }
}