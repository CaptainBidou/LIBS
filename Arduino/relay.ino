int x; 

//the relays connect to
int RelayControl1 = 2; // Digital Arduino Pin used to control the motor
int RelayControl2 = 3;
int RelayControl3 = 4;
int RelayControl4 = 5;
bool RelayControl1State = LOW;
bool RelayControl2State = LOW;
bool RelayControl3State = LOW;
bool RelayControl4State = LOW;

void setup() { 
  pinMode(RelayControl1, OUTPUT);
  pinMode(RelayControl2, OUTPUT);
  pinMode(RelayControl3, OUTPUT);
  pinMode(RelayControl4, OUTPUT);
  digitalWrite(RelayControl1,RelayControl1State);
  digitalWrite(RelayControl2,RelayControl2State);
  digitalWrite(RelayControl3,RelayControl3State);
  digitalWrite(RelayControl4,RelayControl4State);
	Serial.begin(115200); 
	Serial.setTimeout(1); 
} 
void loop() { 


	while (!Serial.available()); //transform as an interruption
	x = Serial.readString().toInt();
  switch(x) {
    case 1:
      RelayControl1State=!RelayControl1State;
      digitalWrite(RelayControl1,RelayControl1State);
      Serial.print(RelayControl2State);
      break;
    case 2:
      RelayControl2State=!RelayControl2State;
      digitalWrite(RelayControl2,RelayControl2State);
      Serial.print(RelayControl2State);
      break;
    case 3:
      RelayControl3State=!RelayControl3State;
      digitalWrite(RelayControl3,RelayControl3State);
      Serial.print(RelayControl3State);
    break;
    case 4:
      RelayControl4State=!RelayControl4State;
      digitalWrite(RelayControl4,RelayControl4State);
      Serial.print(RelayControl4State); 
      break;
  }


//faire la mesure ici 

//envoyer la mesure dans le serial 


} 
