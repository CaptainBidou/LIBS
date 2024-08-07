// get analog value from A0 pin and convert it to temperature ( LM35DZ )
// get value of A1 pin and convert it to temperature, tension divider ( 100k and 100k ) (NTC 100k)



const int ambientSensor = A0;  // Analog input pin that the LM35DZ is attached to
const int surfaceSensor = A1;  // Analog input pin that the NTC 100k is attached to
int ambientTemperature = 0;     // value read from the LM35DZ
float surfaceTemperature = 0; // value read from the NTC 10k

float ADC_coef = 204.6;//number/V    


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

    pinMode(ambientSensor, INPUT);
    pinMode(surfaceSensor, INPUT);
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


// the loop routine runs over and over again forever:
void loop() {
 
  while (!Serial.available()); //transform as an interruption
	x = Serial.readString().toInt();
  switch(x) {
    case 1:
      RelayControl1State=!RelayControl1State;
      digitalWrite(RelayControl1,RelayControl1State);
      Serial.print(RelayControl1State);
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
    case 10:{
      float adc_val = analogRead(ambientSensor);//get the adc value
      float volt = adc_val/ADC_coef;//convert the adc into voltage
      ambientTemperature=volt*100;//convert the voltage into temperature
      Serial.print(ambientTemperature);
      break;

    }
    case 11:{
      float temp = analogRead(surfaceSensor);//get the adc value
      float volt2 = temp / ADC_coef;//convert the adc into voltage
      float resistor = (volt2*10*10*10*10)/(5-volt2);//convert the voltage into resistor
      float logarithm = (25*log(resistor/(10*10*10*10)))+3380000;//compute the denominator value
      surfaceTemperature = (25*3380000)/(logarithm);//compute the temperature value
      Serial.print(surfaceTemperature);
      break;
    }
  }
}