void setup() {  // Ορίζω τις δύο ακίδες 12 και 13 σαν εξόδους:
pinMode(12,OUTPUT);
pinMode(13,OUTPUT);
}

void loop() {  // Ο κώδικας που θέλω να γράψω:
digitalWrite(12,HIGH);//το LED στην ακίδα 12 ανάβει
delay(2000);//μένει αναμμένο για 2 sec
digitalWrite(12,LOW);//το LED στην ακίδα 12 σβήνει και αμέσως ανάβει το επόμενο
digitalWrite(13,HIGH);//το LED στην ακίδα 13 ανάβει
delay(3000);//μένει αναμμένο για 3 sec
digitalWrite(13,LOW);//το LED στην ακίδα 13 σβήνει
}