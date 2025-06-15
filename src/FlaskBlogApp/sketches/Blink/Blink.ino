const int ledPin1 = 2;

// the setup function runs once when you press reset or power the board
void setup() {
  // initialize digital pin LED_BUILTIN as an output.
  pinMode(ledPin1, OUTPUT);
  
  // Start serial communication
  Serial.begin(9600);
}

// the loop function runs over and over again forever
void loop() {
  digitalWrite(ledPin1, HIGH);   // turn the LED on (HIGH is the voltage level)
   Serial.println("LED ON");
  delay(1000);                       // wait for a second
  digitalWrite(ledPin1, LOW);    // turn the LED off by making the voltage LOW
     Serial.println("LED OFF");
  delay(1000);                       // wait for a second
  
  // Send event to serial port
 
}