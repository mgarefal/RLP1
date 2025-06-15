const int monitorPin = 13;
int ledState;
int prevLedState = -1;
int counter = 0;

void setup() {
  pinMode(monitorPin, INPUT);
  Serial.begin(9600);
}

void loop() {
  ledState = digitalRead(monitorPin);

  if (ledState != prevLedState) {
    //if (ledState == HIGH) {
      //Serial.println("PIN13:HIGH");
    //} else {
      //Serial.println("PIN13:LOW");
    //}
    prevLedState = ledState;
    counter++;
    if (counter > 100) {
      counter=0;
    }    		
    delay(50); // debounce delay
  }
  if (Serial.available() > 0) {
    // Read the incoming string from the serial buffer
    String receivedString = Serial.readString();

    // Remove any newline or carriage return characters
    receivedString.trim();

    // Check if the received string is "report"
    if (receivedString == "report") {
        if (counter < 50){
            Serial.println("Counter < 50");
        } else {
          Serial.println("Counter >= 50");
        }
        
      
    }
  }
}