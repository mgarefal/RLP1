unsigned long startTime = 0;
String reportState = "NONE"; // Global variable to store the state

void setup() {
  Serial.begin(9600);
  pinMode(LED_BUILTIN, OUTPUT); // Initialize the built-in LED pin as an output
  startTime = millis(); // Initialize the start time
}

void loop() {
  if (Serial.available() > 0) {
    String command = Serial.readStringUntil('\n'); // Read the incoming command
    if (command.equals("report")) { // Check if the command is "report"
      // Send the report state when requested
      Serial.println(reportState);
    }
  }

  // Check if it's time to update the report state
  unsigned long currentTime = millis();
  if (currentTime - startTime >= 120000) { // 2 minutes = 120000 milliseconds
          reportState = "SUCCESS"; // Set report state to SUCCESS if 2 minutes have passed
      digitalWrite(LED_BUILTIN, HIGH); // Turn on the built-in LED
    
  } else {    
      reportState = "FAILURE"; // Set report state to FAILURE if time hasn't been reached
      digitalWrite(LED_BUILTIN, LOW); // Turn off the built-in LED    
  }
}
