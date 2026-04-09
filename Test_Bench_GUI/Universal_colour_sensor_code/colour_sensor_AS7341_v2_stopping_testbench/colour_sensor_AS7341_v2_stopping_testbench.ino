// Prerequisites:
// Install AS7341 from Arduino Libraries https://github.com/adafruit/Adafruit_AS7341
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

const int num_init_readings_ignore = 15; // ignore the first 15 readings
const int R_buffer_size = 50;         // size of the buffer
uint16_t Array_R_Values[R_buffer_size];  // Array to store 50 latest readings
int index_R_total = 0;                // Number of total R readings recorded
int iteration_R = 0;                  // Number of 50 R-reading cycle
int index_R_array = 0;                // Index in the Array_R_Values
const int derivative_first_threshold = -5000; // threshold for derivative to be negative for the first threshold to be hit
const int derivative_second_threshold = 0;
const int num_consecutive_readings_required = 5; // requires 5 consecutive readings that calculate a derivative that are beyond the threshold
int num_first_threshold = 0; // number of last readings that reached the threshold
int num_second_threshold = 0; // number of last readings that reached the threshold
bool first_threshold_reached = false; // flag for reaching the first threshold
bool second_threshold_reached = false; // flag for reaching the second threshold
bool car_stopped = false;

// default behaviour is to take a span of 15 readings, average the first 5 and last 5, and divide by 10 (midpoints of the two ranges are in between)
const int derivative_span = 15;
const int avg_window = 5;
const int derivative_array_size = 50;
float derivative_R_array[derivative_array_size];
int index_derivative_array = 0;
/*END*/

double PrintSensorReading() {
  redFrequency = as7341.getChannel(AS7341_CHANNEL_555nm_F5); // pick 555nm as the best for sensing
  Serial.print(redFrequency);
  Serial.print(",");

  return redFrequency;
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

  as7341.setLEDCurrent(15); // 4mA // this is in mA, change the current going to the LED as needed.
  as7341.enableLED(true);

  // AS7341 Sensor Configuration setup
  // You can adjust ATIME, ASTEP, and GAIN to increase/decrease sensitivity
  // total acquisition time = (𝐴𝑇𝐼𝑀𝐸 + 1) × (𝐴𝑆𝑇𝐸𝑃 + 1) × 2.78µs (microsecond = 1/1000th of second) 
  // see https://newscrewdriver.com/2023/01/23/notes-on-as7341-integration-time/
  as7341.setATIME(29);
  as7341.setASTEP(599);
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
    // Reset newStartTime - begin recording time as soon as the car starts moving
    newStartTime = millis();
    myservo.writeMicroseconds(safe_angle);

    
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
    // not taking a running average because this sensor is very noise-less
    Array_R_Values[index_R_array] = R_reading;

    if (index_R_total > num_init_readings_ignore) {
      int first_5_avg = 0;
      int last_5_avg = 0;
      for (int i = 0; i < avg_window; i++) {
        int idx = (index_derivative_array + derivative_array_size - (derivative_span-1) + i) % derivative_array_size;
        first_5_avg += Array_R_Values[idx];
      }
      for (int i = 0; i < avg_window; i++) {
        int idx = (index_derivative_array + derivative_array_size - i) % derivative_array_size;
        last_5_avg += Array_R_Values[idx];
      }
      float calculated_derivative = (float)(last_5_avg - first_5_avg) / (derivative_span - avg_window);
      derivative_R_array[index_derivative_array] = calculated_derivative;
      

      // Check for reaching the first threshold and increment if we are.
      if (calculated_derivative < derivative_first_threshold) {
        num_first_threshold++;
      } else {
        num_first_threshold = 0;
      }

      if (num_first_threshold >= num_consecutive_readings_required) {
        first_threshold_reached = true;
      }

      // Check for reaching the second threshold and increment if we are.
      if (first_threshold_reached && (calculated_derivative > derivative_second_threshold)) {
        num_second_threshold++;
      } else {
        num_second_threshold = 0;
      }

      if (first_threshold_reached && (num_second_threshold >= num_consecutive_readings_required)) {
        second_threshold_reached = true;
        
        // STOP THE CAR
        if (car_stopped == false) {
          digitalWrite(motor_relay, LOW);
        }
        
      }

      // Print to Serial Monitor
      Serial.print(calculated_derivative);
      Serial.print(",");
      Serial.print(num_first_threshold);
      Serial.print(",");
      Serial.print(num_second_threshold);
      Serial.print(",");

      Serial.print(first_threshold_reached);
      Serial.print(",");
      Serial.print(second_threshold_reached);
      Serial.print(",");

      if ((car_stopped == false) && (second_threshold_reached == true)) {
        Serial.print("Endpoint Detected");
        Serial.print(",");
      }
      
      // increment derivative tracker index
      index_derivative_array++;
    }

    // increment array tracker index
    index_R_array++;
    index_R_total++;

    // Loop array indices back to 0 if we exceed array size
    if (index_R_array == R_buffer_size) {index_R_array = 0;}

    // Stopping algorithm ***End***

    //Serial.print(timeDiff, DEC);
    Serial.println(" ");

    delay(50);  // ADJUST REPEAT FREQUENCY DELAY - note - limited by ATIME and ASTEP above

    digitalWrite(trans_ctrl, HIGH);
    digitalWrite(LED_BUILTIN, HIGH);

    }
}
