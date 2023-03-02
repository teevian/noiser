byte pin_input = 0;

void setup() {
  Serial.begin(9600);
}

void loop() {

  if(Serial.available() > 0) {
    pin_input = Serial.parseInt();
  }

  if(pin_input >= 0 && pin_input <=5) {
    float value = analogRead(pin_input);
    Serial.println(value * 5 / 1023); 
  }

  delay(1000);
}