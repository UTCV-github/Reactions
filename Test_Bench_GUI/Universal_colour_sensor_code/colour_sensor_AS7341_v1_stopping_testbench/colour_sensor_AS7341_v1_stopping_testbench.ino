// Prerequisites:
// Install AS7341 from Arduion libraries
// Install Board Manager Teensy MicroMod (preferences -> additional board manager urls -> https://www.pjrc.com/teensy/package_teensy_index.json)
// Install Teensy (for Arduino IDE)
// Install INA226_WE from library manager (used for voltage sensor)
// Use Teensy MicroMod board (not Arduino Uno)
// Press Progrma MAode button (BOOT on board)


// Libraries
#include <Servo.h>
#include <Wire.h>
#include <Keyboard.h>
#include <Adafruit_AS7341.h>  // Added AS7341 Library
#include <INA226_WE.h>
#define I2C_ADDRESS 0x40

#define servo_pin 40     // ATP Port G0
const int motor = 0;     // useless declaration
#define button 42        // ATP Port G2
#define button_light 43  // ATP Port G3
#define trans_ctrl 17    // useless
#define motor_relay 41   // ATP Port G1
/*ENDS HERE*/

Adafruit_AS7341 as7341;  // Initialize the AS7341 sensor object
// INA226_WE ina226 = INA226_WE(&Wire1, I2C_ADDRESS); // no current sensor 

double redFrequency = 0;
double greenFrequency = 0;
double blueFrequency = 0;
double clearFrequency = 0;

int counter = 0;
int i = 0;  // Counter variable for taking initial red reading

// Timer variables
int startTime;
double currentTime;
double timeDiff;
double newStartTime = 0;

const int stirrer_rot_speed = 255;

/*Added*/
Servo myservo;  //servo motor
bool released = false;
bool pressed_down = false;
bool logging = false;  // Alternating between T and F after every press of the button

const int start_angle = 2100;
const int pushdown_angle = 1000;
const int safe_angle = 1500;
const int servo_interval = 100;

// Stopping algorithm code
double initialRed = 0;
double R_reading;

const int R_buffer_size = 50;         // size of the buffer
float Array_R_Values[R_buffer_size];  // Array to store 50 latest readings
int index_R_total = 0;                // Number of total R readings recorded
int iteration_R = 0;                  // Number of 50 R-reading cycle
int index_R_array = 0;                // Index in the Array_R_Values

const int RAvg_buffer_size = 15;      // size of the buffer
float Array_R_Avg[RAvg_buffer_size];  // Array to store 15 latest R averages
int index_RAvg_total = 0;             // Number of total R avg calculated
int iteration_RAvg = 0;               // Number of 15 R-Avg cycle
int index_RAvg_array = 0;             // Index in the Array_R_Avg
int num_RAvg = 8;                     // Number of R avg values used when calculating the slope
double R_Avg_slope;
/*END*/

double PrintSensorReading() {
  // Read all channels from the AS7341
  uint16_t readings[12]; 
  // 415nm, 445nm, 480nm, 515nm, Clear, NIR, 555nm, 590nm, 630nm, 680nm, Clear, NIR, 
  if (!as7341.readAllChannels(readings)) {
    Serial.println("Error reading AS7341 sensor");
    return 0;
  }

  // Map AS7341 spectral channels to RGB/Clear equivalents
  // F7 (630nm) or F8 (680nm) can act as Red. We'll use F7 here.
  redFrequency = as7341.getChannel(AS7341_CHANNEL_630nm_F7);
  greenFrequency = as7341.getChannel(AS7341_CHANNEL_515nm_F4);
  blueFrequency = as7341.getChannel(AS7341_CHANNEL_445nm_F2);
  clearFrequency = as7341.getChannel(AS7341_CHANNEL_CLEAR);

  // Print out the sensor readings
  Serial.print(readings[0]);
  Serial.print(",");
  Serial.print(readings[1]);
  Serial.print(",");
  Serial.print(readings[2]);
  Serial.print(",");
  Serial.print(readings[3]);
  Serial.print(",");
  Serial.print(readings[4]);
  Serial.print(",");
  Serial.print(readings[5]);
  Serial.print(",");
  Serial.print(readings[6]);
  Serial.print(",");
  Serial.print(readings[7]);
  Serial.print(",");
  Serial.print(readings[8]);
  Serial.print(",");
  Serial.print(readings[9]);
  Serial.print(",");
  Serial.print(readings[10]);
  Serial.print(",");
  Serial.print(readings[11]);
  Serial.print(",");

  return readings[0];  // temporary - this needs to be changed #TODO 
}

// Button Activity
bool ButtonPress(int button_pin, bool &logging, bool &pressed_down, bool &released, int &i) {
  int servoButton = digitalRead(button_pin);

  if (!servoButton) {  // If the button is pressed down
    pressed_down = true;
    digitalWrite(button_light, HIGH);
    while (pressed_down) {  // While the button is held down
      servoButton = digitalRead(button_pin);
      if (servoButton) {  // If the button is released
        released = true;
        pressed_down = false;
        logging = !logging;  // Toggle logging state
        i = 0;               // Reset the counter
        return true;         // Indicate that the button was pressed and released
      }
    }
  }
  return false;  // Indicate no button press action
}

// Calculate Rolling average of the R readings
double calculateRollingAverage() {
  double sum = 0.0;
  for (int j = 0; j < R_buffer_size; j++) {
    sum += Array_R_Values[j];
  }
  return sum / R_buffer_size;
}

double calculateMovingSlope() {
  double sumFirst = 0.0, sumLast = 0.0;
  for (int j = 0; j < 8; j++) {
    sumLast += Array_R_Avg[(index_RAvg_total - j) % RAvg_buffer_size];                          // The sum of last values in the rolling range
    sumFirst += Array_R_Avg[(index_RAvg_total + 1 - RAvg_buffer_size + j) % RAvg_buffer_size];  // The sum of first values in the rolling range
  }
  return sumFirst - sumLast;
}

void setup() {
  // Setting the outputs
  pinMode(motor_relay, OUTPUT);  // Retained as requested

  pinMode(motor, OUTPUT);
  analogWrite(motor, 0);

  pinMode(trans_ctrl, OUTPUT);
  pinMode(button, INPUT_PULLUP);
  pinMode(button_light, OUTPUT);

  // Servo code (ADDED)
  myservo.attach(servo_pin);
  myservo.writeMicroseconds(start_angle);  // start at 2125

  Serial.begin(115200);                                     // initialize serial - increased to 115200 from 9600
  Serial.println("Checking for AS7341 color sensor...");  // Initial message

  // Check the AS7341 I2C connection
  while (!as7341.begin()) {
    Serial.println("No AS7341 sensor detected. Check wiring/Qwiic cable.");
    delay(2000);  // Check every 2 seconds
  }

  Wire1.begin();
 /* if (!ina226.init()) {
    Serial.println("Failed to init INA226. Check your wiring.");
    while (1) {}
  } */
 // ina226.waitUntilConversionCompleted(); 
  Serial.println("AS7341 sensor detected!");

  as7341.setLEDCurrent(50); // 4mA // this is in mA, change the current going to the LED as needed.
  as7341.enableLED(true);

  // AS7341 Sensor Configuration setup
  // You can adjust ATIME, ASTEP, and GAIN to increase/decrease sensitivity
  as7341.setATIME(100);
  as7341.setASTEP(999);
  as7341.setGain(AS7341_GAIN_256X);
}

void loop() {
  float shuntVoltage_mV = 0.0;
  float loadVoltage_V = 0.0;
  float busVoltage_V = 0.0;
  float current_mA = 0.0;
  float power_mW = 0.0;

 /* ina226.readAndClearFlags();
  shuntVoltage_mV = ina226.getShuntVoltage_mV();
  busVoltage_V = ina226.getBusVoltage_V();
  current_mA = ina226.getCurrent_mA();
  power_mW = ina226.getBusPower();
  loadVoltage_V  = busVoltage_V + (shuntVoltage_mV / 1000); */

  char input = Serial.read();
  bool Button_Pressed = ButtonPress(button, logging, pressed_down, released, i);  // Check if the button is pressed

  
  if (input == 115) { // 115 = "s"
    logging = true;
    i = 0;  // reset counter i
  }

  if (input == 116) { // 116 = "t"
    logging = false;
  }

  if (input == 112) { // 112 = "p"
    // here we are just responding to ping from the python code. Respond with a confirmationcode. 
    Serial.println("Checking for AS7341 color sensor...");
  }

  // if (Button_Pressed) {  //if button has been pressed and released
  if ((Button_Pressed && logging) || input == 115) {  //if button has been pressed and released
    Serial.println("\nREACTION REACTION REACTION");
    released = false;

    myservo.writeMicroseconds(pushdown_angle);

    delay(1000);
    digitalWrite(motor_relay, HIGH);

    myservo.writeMicroseconds(safe_angle);

    // Reset newStartTime
    newStartTime = millis();

    // Time Sensor Delay for car - syringe 
    // // Have a 3 s delay between pressing the button and adding the starting chemical
    // while (i < 6) {
    //   i++;

    //   // Obtain initial red frequency values from AS7341
    //   as7341.readAllChannels();
    //   initialRed = as7341.getChannel(AS7341_CHANNEL_630nm_F7);

    //   Serial.print("R: ");
    //   Serial.print(initialRed, DEC);
    //   Serial.println(" ");  // Print out the red value
    //   delay(500);           //Delay 0.5 sec between each reading

    //   // Check Input/button activity
    //   input = Serial.read();
    //   if (input == 116) {
    //     logging = false;
    //   }

    //   if (ButtonPress(button, logging, pressed_down, released, i) || input == 116) {
    //     delay(100);
    //     break;
    //   }

    //   // If all 6 R initial reading are printted, print the start msg
    //   if (i == 6) {
    //     newStartTime = millis();  // Obtain a new starttime
    //     Serial.println("Reaction Starts Now!");
    //   }
      // }
  }

  else if ((logging == false)) {  //Skip the printing part if logging is false
    return;
  }

  /***** ENDS HERE *******/
  else {
    // Timer
    currentTime = millis();
    timeDiff = (currentTime - newStartTime) / 1000;
    Serial.print(timeDiff);
    Serial.print(",");
    R_reading = PrintSensorReading();

    // Serial.print("Shunt Voltage [mV]: "); Serial.println(shuntVoltage_mV);
    // Serial.print("Bus Voltage [V]: "); Serial.println(busVoltage_V);
    // Serial.print("Load Voltage [V]: "); Serial.println(loadVoltage_V);
    // Serial.print("Current[mA]: "); Serial.println(current_mA);
    // Serial.print("Bus Power [mW]: "); Serial.println(power_mW);
/*    if (!ina226.overflow)
    {
      Serial.println("Values OK - no overflow");
    }
    else
    {
      Serial.println("Overflow! Choose higher current range");
    }
    Serial.println(); */ 

    // Stopping algorithm ***Start***
    
    // Stopping algorithm ***End***

    //Serial.print(timeDiff, DEC);
    Serial.println(" ");

    delay(50);  // adjust how frequently you want the colours to update; decided 0.3 s was optimal

    digitalWrite(trans_ctrl, HIGH);
    digitalWrite(LED_BUILTIN, HIGH);

    }
}
