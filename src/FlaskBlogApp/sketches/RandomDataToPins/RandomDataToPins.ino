#define DIGITAL_PIN_START 2
#define DIGITAL_PIN_END 13
#define ANALOG_PIN_START A0
#define ANALOG_PIN_END A5

void setup() {
    // Set digital pins 2-13 as outputs
    for (int i = DIGITAL_PIN_START; i <= DIGITAL_PIN_END; i++) {
        pinMode(i, OUTPUT);
    }

    // Set analog pins A0-A5 as outputs (though they are normally input, we use PWM on PWM-capable pins)
}

void loop() {
    // Randomly turn digital pins on/off
    for (int i = DIGITAL_PIN_START; i <= DIGITAL_PIN_END; i++) {
        digitalWrite(i, random(2)); // Randomly sets HIGH (1) or LOW (0)
    }

    // Randomly set PWM values to analog pins (0-255)
    for (int i = ANALOG_PIN_START; i <= ANALOG_PIN_END; i++) {
        int pwmValue = random(256); // Random value between 0 and 255
        analogWrite(i, pwmValue);  // Apply PWM to the analog pin
    }

    // Wait 60 seconds before repeating
    delay(60000);
}