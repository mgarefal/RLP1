void setup() {
  Serial.begin(9600);
}

void loop() {
  
  if (Serial.available() > 0) {
    // Read the incoming string from the serial buffer
    String receivedString = Serial.readString();

    // Remove any newline or carriage return characters
    receivedString.trim();

    // Check if the received string is "report"
    if (receivedString == "report") {
        Serial.println("PASSED");
    }
  }  
}