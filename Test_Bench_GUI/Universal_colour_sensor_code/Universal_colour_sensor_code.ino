#include <Wire.h>
#include "Adafruit_TCS34725.h"
#include "Keyboard.h"
float threshold = 5;
float largerThreshold = 10;
float thresholdZero = 500;
float startTime;
float currentTime;
float timeDiff;
int Started = 0;
int ending = 0;
int initValue = 1;

long long overallSum = 0;
int overallMeasurements = 0;
int overallAvg = 0;
int read_idx = 0;
long larger_diff = 0;
int MAX_IDX = 10;
long int cur_sum = 0;
int cur_tf[11];
long cur_avg = 0;
int prev_tf[11];
int averages[11];
int prev_sum = 0;
long prev_avg = 0;
long first_diff = 0;
float measured_time = 0;

/* Connect SCL to analog 5
Connect SDA to analog 4
Connect VDD to 3.3V DC
Connect GROUND to common ground */
/* Initialise with default values (int time = 2.4ms, gain = 1x) */
//TCS34725_INTEGRATIONTIME_154MS for a max of 65525 reading, TCS34725_INTEGRATIONTIME_120MS can only yield 51200
Adafruit_TCS34725 tcs = Adafruit_TCS34725(TCS34725_INTEGRATIONTIME_154MS, TCS34725_GAIN_1X);
/* Initialise with specific int time and gain values */

// Car Motor
const int car_motor_speed = 5;
const int car_motor_fwd = 8; 
const int car_motor_rev = 9;

//Stirrer

const int stirrer_speed = 9;
//const int stirrer_fwd = 6;
//const int stirrer_rev = 7;


// button

void setup(void) {
  
    Serial.begin(9600);

    if (tcs.begin()) {
      Serial.println("Found sensor");
    } else {
      Serial.println("No TCS34725 found ... check your connections");
      while (1);
    }
// Now we're ready to get readings!
    //setup queue
    for (int i = 0; i < (MAX_IDX + 1); i++){
      cur_tf[i] = 0;
      prev_tf[i] = 0;
      averages[i] = 0;
    }
    // Car Motor Setup
    pinMode(car_motor_speed, OUTPUT);
    pinMode(car_motor_fwd, OUTPUT);
    pinMode(car_motor_rev, OUTPUT);

    // Stirrer Setup

    pinMode(stirrer_speed, OUTPUT);
    //pinMode(stirrer_fwd, OUTPUT);
    //pinMode(stirrer_rev, OUTPUT);
    
    // Car motor initialization
    digitalWrite(car_motor_fwd, LOW);
    digitalWrite(car_motor_rev, LOW);
    analogWrite(car_motor_speed, 255);

    // stirrer initialization
    //digitalWrite(stirrer_fwd, LOW);
    //digitalWrite(stirrer_rev, LOW);
    analogWrite(stirrer_speed, 0);

}


void loop(void) {
uint16_t r, g, b, c, colorTemp, lux;
if(Serial.available()){
    char input = Serial.read();
  // Type letters into the serial monitor to access various options
    if (input == 115){
        // s: Start the car, including the stirrer and the main motor
        startTime = millis();
        digitalWrite(car_motor_fwd, HIGH);
        digitalWrite(car_motor_rev, LOW);
        //digitalWrite(stirrer_fwd, HIGH);
        //digitalWrite(stirrer_rev, LOW);
        analogWrite(stirrer_speed, 80);
        Started = 1;
        initValue = 1;
    }
    if (input == 114){
        // r: Restart the car motor, keeping the current timer
        digitalWrite(car_motor_fwd, HIGH);
        digitalWrite(car_motor_rev, LOW);
        Started = 1;
    }
    if (input == 116){
        // t: Stops the car and measurement, including timers
        currentTime = millis();
        timeDiff = currentTime - startTime;
        // Serial.print("Time (Interrupt): "); Serial.print(timeDiff/1000, DEC);
        // Serial.println(" ");
        // Car motor initialization
        digitalWrite(car_motor_fwd, LOW);
        digitalWrite(car_motor_rev, LOW);
        analogWrite(car_motor_speed, 255);
    
        // stirrer initialization
        //digitalWrite(stirrer_fwd, LOW);
        //digitalWrite(stirrer_rev, LOW);
        analogWrite(stirrer_speed, 0);
        Started = 0;
    }
}


if(Started){
    tcs.getRawData(&r, &g, &b, &c);
    currentTime = millis();
    timeDiff = currentTime - startTime;
    if(timeDiff > 5000){
        //digitalWrite(stirrer_fwd, LOW);
        //digitalWrite(stirrer_rev, LOW);  
        digitalWrite(stirrer_speed, 0);
    }

    

    cur_tf[read_idx] = c;
    cur_sum = 0;
    for (int i = 0; i < (MAX_IDX + 1); i++){
      cur_sum += cur_tf[i];
    }

    if (timeDiff > 6000 & timeDiff < 10000) {
      overallSum += cur_tf[read_idx];
      overallMeasurements++;
      overallAvg = overallSum/overallMeasurements;
    }
    
    cur_avg = cur_sum / (MAX_IDX + 1);
    averages[read_idx] = cur_avg;

    prev_sum = 0;
    for (int i = 0; i < (MAX_IDX + 1); i++){
      prev_sum += prev_tf[i];
    }

    prev_avg = prev_sum / (MAX_IDX + 1);
    
    first_diff = cur_avg - prev_avg;
    if (read_idx - 4 < 0) {
      larger_diff = averages[read_idx] - averages[read_idx + 11 - 4];
    } else {
      larger_diff = averages[read_idx] - averages[read_idx - 4];
    }
    if(initValue){
      if(timeDiff > 20000){
        initValue=0;
        }
    }else{
//      if((ending <1) & ((larger_diff > largerThreshold) | (cur_avg - overallAvg) > thresholdZero)){
        if((ending >1) & ((larger_diff > largerThreshold) | (cur_avg - overallAvg) > thresholdZero)){
        // Car motor initialization
        Serial.print("Measured Time: ");
        Serial.print(timeDiff/1000, DEC);
        Serial.println(" ");
        // // Car motor initialization
        // digitalWrite(car_motor_fwd, LOW);
        // digitalWrite(car_motor_rev, LOW);
        // digitalWrite(stirrer_fwd, LOW);
        // digitalWrite(stirrer_rev, LOW);
        measured_time = timeDiff;
        // Started = 0;
        ending = 20;
      }else if(ending == 1){
        Started = 0;
        measured_time = 0;
        ending = 0;
        overallSum = 0;
        overallMeasurements = 0;
        overallAvg = 0;
        // Car motor initialization
        digitalWrite(car_motor_fwd, LOW);
        digitalWrite(car_motor_rev, LOW);
        //digitalWrite(stirrer_fwd, LOW);
        //digitalWrite(stirrer_rev, LOW);
      }else{
        ending = ending -1;
      }
    }
    prev_tf[read_idx] = c;
    read_idx++;
    if (read_idx > MAX_IDX){
      read_idx = 0;
    }
    
    
//    if(c>(threshold+initialCValue)){
//        Serial.print("Measured Time: ");
//        Serial.print(timeDiff/1000, DEC);
//        Serial.println(" ");
//        // Car motor initialization
//        digitalWrite(car_motor_fwd, LOW);
//        digitalWrite(car_motor_rev, LOW);
//        digitalWrite(stirrer_fwd, LOW);
//        digitalWrite(stirrer_rev, LOW);
//        Started = 0;
//    }
    Serial.print("R:"); Serial.print(r, DEC); Serial.print(", ");
    Serial.print("G:"); Serial.print(g, DEC); Serial.print(", ");
    Serial.print("B:"); Serial.print(b, DEC); Serial.print(", ");
    Serial.print("C:"); Serial.print(c, DEC); Serial.print(", ");
    // Serial.print("cur_avg:"); Serial.print(cur_avg, DEC); Serial.print(", ");
    // Serial.print("prev_avg:"); Serial.print(prev_avg, DEC); Serial.print(", ");
    // Serial.print("read_idx:"); Serial.print(read_idx, DEC); Serial.print(", ");
    Serial.print("Time:"); Serial.print(timeDiff/1000, DEC); Serial.print(", ");
    // Serial.print("Measured Time:"); Serial.print(measured_time/1000, DEC); Serial.print(", ");
    // Serial.print("Averages: ");
    // for (int i = 0; i < (MAX_IDX + 1); i++) {
    //   Serial.print(averages[i], DEC); Serial.print("; ");
    // }
    // Serial.print(", ");
    // //Serial.print("Checking"); Serial.print((read_idx - 4) % 11, DEC); Serial.print(", ");
    // Serial.print("First Diff:"); Serial.print(first_diff, DEC); Serial.print(", ");
    // Serial.print("Larger Diff:"); Serial.print(larger_diff, DEC); Serial.print(", ");
    // Serial.print("Overallavg:"); Serial.print(overallAvg, DEC); Serial.print(", ");
    // Serial.print("Delta0:"); Serial.print((cur_avg - overallAvg), DEC); Serial.print(", ");
//    if (first_diff > threshold) {
//      Serial.print("Delta reached and stopped");
//    } else {
//      Serial.print("Delta not reached");
//    }
    
    Serial.println(" ");
  }
}
