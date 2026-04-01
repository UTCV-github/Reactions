// Libraries 
#include <Servo.h>
#include <Wire.h>
#include <Keyboard.h>

#define S0 4
#define S1 5
#define S2 6
#define S3 7
#define S4 3 // this was used for stirring 
#define sensorOut 8
#define button 13

/*ADDED CODE*/
#define servo_pin 9
/*ENDS HERE*/

int redFrequency = 0;
int greenFrequency = 0;
int blueFrequency = 0;
int clearFrequency = 0;
int counter = 0;
int i = 0;       // Counter variable for taking initial red reading

// Timer variables
int startTime;
double currentTime;
double timeDiff;
double newStartTime = 0;

const int stirrer_rot_speed = 255;

const int trans_ctrl = 10; // Connect pwm pin to pin 10
const int motor = 11;
/*Added*/
Servo myservo; //servo motor
bool released = false;
bool pressed_down = false;
bool logging = false; // Alternating between T and F after every press of the button

const int max_angle = 120; 
const int safe_angle = 50;
const int servo_delay = 40; // default 40 
const int servo_interval = 10;

// Stopping algrithm code
double initialRed = 0;
double R_reading;

const int R_buffer_size = 50; // size of the buffer
float Array_R_Values[R_buffer_size]; // Array to store 50 latest readings
int index_R_total = 0; // Number of toal R readings recorded
int iteration_R = 0; // Number of 50 R-reading cycle
int index_R_array = 0; // Index in the Array_R_Values

const int RAvg_buffer_size = 15; // size of the buffer
float Array_R_Avg[RAvg_buffer_size]; // Array to store 15 latest R averages
int index_RAvg_total = 0; // Number of total R avg calculated
int iteration_RAvg = 0; // Number of 15 R-Avg cycle
int index_RAvg_array = 0; // Index in the Array_R_Avg
int num_RAvg = 8; // Number of R avg values used when calculating the slope
double R_Avg_slope;
/*END*/

// Stopping algorithm code variables v2
int readingCount = 0;
const int memoryLength = 25;
double greenData[memoryLength][4] = {0}; // rows, columns 
int runningSum = 0; // running sum of green values ^3 
const int derivativeMemoryLength = 100; // keep a longer record of the last derivatives (10s)
bool derivativeMemory[derivativeMemoryLength] = {0}; // memory of the last derivatives - positive slope is True, negative slope is False
int derivativeReadingCount = 0;
int derivativeCountBuffer = 50; // make sure the last 5 seconds have been either negative or positive
bool derivativeThreshold = 0.95; // 95% 
bool positiveFlag = false;
bool positive_derivative_slope_threshold = 0;


void PrintSensorReading(double* current_reading){
  // Setting RED (R) filtered photodiodes to be read
    digitalWrite(S2,LOW);
    digitalWrite(S3,LOW);
  
    // Reading the output frequency
    redFrequency = pulseIn(sensorOut, LOW);
    
    // Setting GREEN (G) filtered photodiodes to be read
    digitalWrite(S2,HIGH);
    digitalWrite(S3,HIGH);
    
    // Reading the output frequency
    greenFrequency = pulseIn(sensorOut, LOW);
  
    // Setting BLUE (B) filtered photodiodes to be read
    digitalWrite(S2,LOW);
    digitalWrite(S3,HIGH);
    
    // Reading the output frequency
    blueFrequency = pulseIn(sensorOut, LOW);

    // Setting Clear (C) filtered photodiodes to be read
    digitalWrite(S2,HIGH);
    digitalWrite(S3,LOW);

    // Reading the output frequency
    clearFrequency = pulseIn(sensorOut, LOW);

    // Print out the sensor readings as "R,G,B,C\n"
    Serial.print(redFrequency, DEC); Serial.print(",");
    Serial.print(greenFrequency, DEC); Serial.print(",");
    Serial.print(blueFrequency, DEC); Serial.print(",");
    Serial.print(clearFrequency, DEC); Serial.print(",");

    // current_reading[0] = redFrequency;
    // current_reading[1] = greenFrequency;
    // current_reading[2] = blueFrequency;
    // current_reading[3] = clearFrequency;
    current_reading[0] = greenFrequency;
}

// Button Activity
bool ButtonPress(int button_pin, bool &logging, bool &pressed_down, bool &released, int &i) {
    int servoButton = digitalRead(button_pin);

    if (!servoButton) { // If the button is pressed down
        pressed_down = true;
        while (pressed_down) { // While the button is held down
            servoButton = digitalRead(button_pin);
            if (servoButton) { // If the button is released
                released = true;
                pressed_down = false;
                logging = !logging; // Toggle logging state
                i = 0; // Reset the counter
                return true; // Indicate that the button was pressed and released
            }
        }
    }
    return false; // Indicate no button press action
}

// Calculate Rolling average of the R readings
double calculateRollingAverage() {
    double sum = 0.0;
    for (int i = 0; i < R_buffer_size; i++) {
        sum += Array_R_Values[i];
    }
    return sum / R_buffer_size;
}

double calculateMovingSlope() {
    double sumFirst = 0.0, sumLast = 0.0;
    for (int i = 0; i < 8; i++) {
        sumLast += Array_R_Avg[(index_RAvg_total - i) % RAvg_buffer_size]; // The sum of last values in the rolling range
        sumFirst += Array_R_Avg[(index_RAvg_total + 1 - RAvg_buffer_size + i) % RAvg_buffer_size]; // The sum of first values in the rolling range
    }
    return sumFirst - sumLast;
}

void setup() {
  // Color Sensor Code
  // Setting the outputs
  pinMode(S0, OUTPUT);
  pinMode(S1, OUTPUT);
  pinMode(S2, OUTPUT);
  pinMode(S3, OUTPUT);
  pinMode(S4, OUTPUT); // transistor ?
  
  // Setting the sensorOut as an input
  pinMode(sensorOut, INPUT);
  
  pinMode(motor, OUTPUT);
  analogWrite(motor, 0);

  pinMode(trans_ctrl, OUTPUT);

  digitalWrite(13, INPUT_PULLUP);

  // Setting frequency scaling to 20%
  digitalWrite(S0,HIGH);
  digitalWrite(S1,LOW);

  // Servo code (ADDED)
  myservo.attach(servo_pin);
  myservo.write(max_angle); //initializes the angle to 120
  
  Serial.begin(9600);         // initialize serial
  
  Serial.println("Checking for TCS3200 color sensor..."); // Initial message
  
  // Check the color sensor connection until connected
  while (true) {
    // Set S2 and S3 to detect red frequency
    digitalWrite(S2, LOW);
    digitalWrite(S3, LOW);

    // Measure the frequency on the sensorOut pin
    unsigned long pulseLength = pulseIn(sensorOut, LOW, 500); // 100ms timeout

    if (pulseLength > 0) {
      // If a valid pulse is detected, the sensor is connected
      Serial.println("Color sensor detected");
      break; // Exit the loop
    } else {
      // No pulse detected, sensor might not be connected
      Serial.println("No color sensor detected");
    }

    delay(2000); // Check every 2 second
  }

  // Initialize to 0
  for (int i = 0; i < memoryLength; i++) {
    for (int j = 0; j < 4; j++) {
      greenData[i][j] = 0;
      Serial.println(greenData[i][j]);
    }
  }
}

void loop() {
  char input = Serial.read();
  bool Button_Pressed = ButtonPress(button, logging, pressed_down, released, i); // Check if the button is pressed

  if (input == 115){
    logging = true;
    i = 0; // reset counter i
  }

  if (input == 116){
    logging = false;
  }

  // if (released && logging){ //if button has been pressed and released
  if ((Button_Pressed && logging) || input == 115){ //if button has been pressed and released 
    Serial.println("\nREACTION REACTION REACTION");
    released = false;


    // Skip the servo delay - don't need this for non-injection system
    if (false) {
      for (int i = max_angle ; i>-20 ; i -= servo_interval){
        //i sets the degree of rotation for the servo - must change it depending on delay (speed) set
        if(i < 0) { myservo.write(0); }
        myservo.write(i);
        //delays to give time to the servo to rotate -- reduce number inside to make it spin faster (controls the speed)
        delay(servo_delay);
      }
      delay(servo_delay+1000);

      // Start Stirring
      digitalWrite(S4, HIGH); 
    }
    //safe angle, after the servo goes 120, goes back to 50 degrees
    for (int i = -5 ; i<safe_angle ; i += servo_interval/2){
      myservo.write(i); //min_angle
      delay(servo_delay);
    }
    
    digitalWrite(S2,LOW);
    digitalWrite(S3,LOW);

    newStartTime = millis(); // Obtain a new starttime
    Serial.println("Reaction Starts Now!");
  }

  else if ((logging == false)){ //Skip the printing part if logging is false 
      // Serial.println("\nWAITING");
      return;
    }

/***** ENDS HERE *******/
  else{
    // Time, R, G, B, C, Average Derivative over last 25 entries, 
    // Timer
    currentTime = millis();
    timeDiff = (currentTime - newStartTime)/1000;

    Serial.print(timeDiff, DEC);
    Serial.print(",");

    // STOPPING ALGORITHM
    
    PrintSensorReading(greenData[readingCount]);

    // calculate third power, then calculate the running average
    int thirdPower = pow(greenData[readingCount][0], 3);
    double derivatives[memoryLength] = {0};
    int derivativeSum = 0;
    runningSum -= greenData[readingCount][1]; // subtract the last element from the sum.
    greenData[readingCount][1] = thirdPower; // 1st column is the third power
    runningSum += thirdPower; // add the last element to the sum
    greenData[readingCount][2] = runningSum / memoryLength; // average out the last {25} readings (i.e., last 2.5 seconds since 0.100 ms between readings)

    // derivative calculation algorithm: take average of last {25} derivatives:
    for(i = 0; i < memoryLength; i++) {
      int index = (readingCount - (i + 1) + memoryLength) % memoryLength; // the next index to calculate derivative against
      derivatives[i] = (greenData[readingCount][2] - greenData[index][2]) / (i + 1);
      derivativeSum += derivatives[i];
    }
    // write the average derivative to the 4th column
    greenData[readingCount][3] = derivativeSum / memoryLength;
    // write true (positive slope) or false (negative slope) to the derivative memory
    derivativeMemory[derivativeReadingCount] = (greenData[readingCount][3] > positive_derivative_slope_threshold);
    Serial.print(greenData[readingCount][3], 2);
    Serial.print(",");
    Serial.print(derivativeMemory[derivativeReadingCount], 2);
    Serial.print(",");

    // Check if the last {derivativeCounterBuffer} values have been 95% positive:
    int number_positive_derivatives = 0;

    for (int i = 0; i < derivativeCountBuffer; i++) {
        int index = (derivativeReadingCount - i + derivativeMemoryLength) % derivativeMemoryLength;
        number_positive_derivatives += derivativeMemory[index];  // using column 2 as in your earlier code
    }
    Serial.print(number_positive_derivatives);
    Serial.print(",");
    double percent_last_positive = (double)number_positive_derivatives / derivativeCountBuffer; // have to cast to numerical first
    Serial.print(percent_last_positive, 3);
    Serial.println(",");
    

    if (!positiveFlag && percent_last_positive > derivativeThreshold) {
      positiveFlag = true;
      Serial.println("positive_flag_set");
    }
    if (positiveFlag && percent_last_positive < (1 - derivativeThreshold)) { // maybe I should separate the up threshold from the down threshold
      positiveFlag = false;
      Serial.println("ENDPOINT_DETECTED,");
    }

    readingCount++;
    derivativeReadingCount++;
    if (readingCount == memoryLength){readingCount = 0;} // wrap counter to 0
    if (derivativeReadingCount == derivativeMemoryLength){derivativeReadingCount = 0;}
    // END OF STOPPING ALGORITHM
    delay(50); // adjust how frequently you want the colours to update; decided 0.3 s was optimal


    analogWrite(trans_ctrl, 255);
    digitalWrite(LED_BUILTIN, HIGH);
  }
}
