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

    counter++;
    if (counter>=500000){
	counter=0;
	}
    Serial.println(counter);			
    delay(50); // debounce delay
    
}