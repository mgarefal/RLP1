const int monitorPin = 6;
int ledState;
int prevLedState = -1;
int counter = 0;
int counter2=0;

void setup() {
  pinMode(monitorPin, INPUT);
  Serial.begin(9600);
}

void loop() {
  ledState = digitalRead(monitorPin);

  if (ledState != prevLedState) {
    prevLedState = ledState;
    counter=counter+1;
    if (counter > 10000) {
      counter=0;
      counter2=counter2+1;
    }    		
    delay(3); // debounce delay
  }
  if (Serial.available() > 0) {
    // Read the incoming string from the serial buffer
    String receivedString = Serial.readString();

    // Remove any newline or carriage return characters
    receivedString.trim();

    // Check if the received string is "report"
    if (receivedString == "report") {
       Serial.println("Counter:" + String(counter) + "Counter2:" + String(counter2));             
      }
   }
}