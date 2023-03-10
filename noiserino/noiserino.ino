byte pin_input = 0;

const uint8_t A[6];   // analog input values
String boardInfo;     // string to store board information
bool stopReading = false;
int analogPin;

void setup() {
  Serial.begin(9600);
  randomSeed(analogRead(0));  // seed the random number generator with an analog input value


}

void loop() {
  if(!stopReading) {
    if(Serial.available() > 0) {
      analogPin = Serial.parseInt();

      int value;
      while(!stopReading) {
        value = analogRead(analogPin);
        Serial.println(value);
        if(Serial.available() > 0) {
          String command = Serial.readStringUntil('\n');
          if(command == "STOP\n") {
            stopReading = true;
          }
        }
      }
    }
  }

  if (Serial.available() > 0) {
    String command = Serial.readStringUntil('\n'); // read command from Noisr
    command.trim(); // remove whitespace

    if(command == "handshake") {
      // send random number to tell its ok!
      Serial.print(random(20));
    } else if(command = "0") {
      pin = Serial.parseInt();
      int value = analogRead(pin)
      Serial.print(value)
    }

    delay(1000);
}
}
/*
    if(command == "handshake") {
      // send random number to tell its ok!
      Serial.print(random(20));
    } else if(command == "info") {
      // send board information
      boardInfo = "Board type: ";
#if defined(__AVR_ATmega328P__)
      boardInfo += "Arduino Uno";
#elif defined(__AVR_ATmega2560__)
      boardInfo += "Arduino Mega";
#elif defined(__AVR_ATmega32u4__)
      boardInfo += "Arduino Leonardo"
#else
      boardInfo += "Unknown";
#endif
      Serial.print(boardInfo);
    }
  }
/*
  if(pin_input >= 0 && pin_input <=5) {
    float value = analogRead(pin_input);
    Serial.println(value * 5 / 1023); 
  }
*/


