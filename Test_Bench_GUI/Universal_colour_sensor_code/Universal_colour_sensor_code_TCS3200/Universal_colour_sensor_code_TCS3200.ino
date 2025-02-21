// Libraries 
#include <Servo.h>
#include <Wire.h>
#include <Keyboard.h>

#define S0 4
#define S1 5
#define S2 6
#define S3 7
#define S4 3
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

int startTime;
double currentTime;
double timeDiff;

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
const int servo_delay = 40;
const int servo_interval = 10;

double initialRed = 0;
double dRed = 0;
double newStartTime = 0;
/*END*/

double PrintSensorReading(double initialRed){
  // Setting RED (R) filtered photodiodes to be read
    digitalWrite(S2,LOW);
    digitalWrite(S3,LOW);
  
    // Reading the output frequency
    redFrequency = pulseIn(sensorOut, LOW);
    dRed = abs(redFrequency - initialRed);
    
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

    // Print out the sensor readings
    Serial.print("R: "); Serial.print(redFrequency, DEC); Serial.print(" ");
    Serial.print("G: "); Serial.print(greenFrequency, DEC); Serial.print(" ");
    Serial.print("B: "); Serial.print(blueFrequency, DEC); Serial.print(" ");
    Serial.print("C: "); Serial.print(clearFrequency, DEC); Serial.print(" ");
    Serial.println(" ");

    return dRed;
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
  myservo.write(0); //initializes the angle to 0
  
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

    for (int i = max_angle ; i>-20 ; i -= servo_interval){
      //i sets the degree of rotation for the servo - must change it depending on delay (speed) set
      if(i < 0) { myservo.write(0); }
      myservo.write(i);
      //delays to give time to the servo to rotate -- reduce number inside to make it spin faster (controls the speed)
      delay(servo_delay);
    }
    delay(servo_delay+1000);
    digitalWrite(S4, HIGH);
    
    //safe angle, after the servo goes 120, goes back to 50 degrees
    for (int i = -5 ; i<safe_angle ; i += servo_interval/2){
      myservo.write(i); //min_angle
      delay(servo_delay);
    }
    
    digitalWrite(S2,LOW);
    digitalWrite(S3,LOW);

    // Have a 3 s delay between pressing the button and adding the starting chemical
    while (i < 6) {
      i++;
      initialRed = pulseIn(sensorOut, LOW); // obtain initial red frequency values
      Serial.print("R: "); Serial.print(initialRed, DEC); Serial.println(" "); // Print out the red value
      delay(500); //Delay 0.5 sec between each reading 

      // Check Input/button activity
      input = Serial.read();
      if (input == 116){
        logging = false;
      }
      
      if (ButtonPress(button, logging, pressed_down, released, i) || input == 116){
        delay(100);
        break;
      }

      // If all 6 R initial reading are printted, print the start msg
      if (i == 6){
        newStartTime = millis(); // Obtain a new starttime
        Serial.println("Reaction Starts Now!");
      }
    }
  }

  else if ((logging == false)){ //Skip the printing part if logging is false 
      // Serial.println("\nWAITING");
      return;
    }

/***** ENDS HERE *******/
  else{
    // Timer
    currentTime = millis();
    timeDiff = (currentTime - newStartTime)/1000;

    dRed = PrintSensorReading(initialRed);
    delay(300); // adjust how frequently you want the colours to update; decided 0.3 s was optimal
    Serial.print(dRed);

  // // Stopping algorithm
  // if ((dRed >= 35) && (timeDiff>20)){
  //   counter += 1;
  //   if (counter == 3){
  //     analogWrite(motor, 0);
  //     Serial.print("Reaction Over!!");
  //     Serial.println(" ");
  //     Serial.print("Final Time Diff:"); Serial.print(timeDiff, DEC);
  //     while(true);
  //   }
  // } else{ //Ensures change occurs 3 consecutive times 
  //   counter = 0;
  // }

    analogWrite(trans_ctrl, 255);
    digitalWrite(LED_BUILTIN, HIGH);

    Serial.print("|| Time Diff:"); Serial.print(timeDiff, DEC);
    Serial.println(" ");
  }
}
