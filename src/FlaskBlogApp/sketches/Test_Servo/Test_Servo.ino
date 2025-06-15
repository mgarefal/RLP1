#include <Servo.h>

Servo myservo;  // create a Servo object

void setup() {
  myservo.attach(5);  // attach the servo to digital pin 5
}

void loop() {
  myservo.write(90);  // set the servo position to 90 degrees
  delay(3000);        // wait for 1 second
  myservo.write(180);   // set the servo position to 0 degrees
  delay(3000);        // wait for 1 second
  myservo.write(0);   // set the servo position to 0 degrees
  delay(3000);        // wait for 1 second
}