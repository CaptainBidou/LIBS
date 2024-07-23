// get analog value from A0 pin and convert it to temperature ( LM35DZ )
// get value of A1 pin and convert it to temperature, tension divider ( 100k and 100k ) (NTC 100k)



const int ambientSensor = A0;  // Analog input pin that the LM35DZ is attached to
const int surfaceSensor = A1;  // Analog input pin that the NTC 100k is attached to
int ambientTemperature = 0;     // value read from the LM35DZ
float surfaceTemperature = 0;     // value read from the NTC 10k

void setup() {

    pinMode(ambientSensor, INPUT);
    pinMode(surfaceSensor, INPUT);
    Serial.begin(9600);

}


// the loop routine runs over and over again forever:
void loop() {
  float ADC_coef = 204.6;//number/V

  float adc_val = analogRead(ambientSensor);//get the adc value
  float volt = adc_val/ADC_coef;//convert the adc into voltage
  ambientTemperature=volt*100;//convert the voltage into temperature
  
  float temp = analogRead(surfaceSensor);//get the adc value
  volt = temp / ADC_coef;//convert the adc into voltage
  float resistor = (volt*10*10*10*10)/(5-volt);//convert the voltage into resistor
  float logarithm = (25*log(resistor/(10*10*10*10)))+3380000;//compute the denominator value
  surfaceTemperature = (25*3380000)/(logarithm);//compute the temperature value



  Serial.print("Ambient temperature: ");
  Serial.print(ambientTemperature);
  Serial.print(" C\n");
  Serial.print("Surface temperature: ");
  Serial.print(surfaceTemperature);
  Serial.println(" C\n");
  delay(1000);

}