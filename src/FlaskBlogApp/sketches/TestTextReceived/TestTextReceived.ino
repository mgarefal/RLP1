void setup() {
  // Initialize the serial communication with a baud rate of 9600
  Serial.begin(9600);
  while (!Serial) {
    ; // Wait for the serial port to connect (only needed for some boards)
  }
}

void loop() {
  // Check if any data is available to read from the serial port
  if (Serial.available() > 0) {
    // Read the incoming data as a string
    String receivedData = Serial.readStringUntil('\n');
    
    // Send the received data back to the sender
    Serial.println("Received: " + receivedData);
  }
}