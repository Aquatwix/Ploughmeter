/*
  Project Name: Ploughmeter
  Description: Data acquisition from ploughmeter sensors and RF transmission at 169MHz.
  Author: Dorian Poissonnet
  Created: 2023, May 30
  Version: v1.0
  Required Hardware: Fether Huzzah ESP8266, MAX31865 + PT100, ICM20948, 

  Used Libraries:
  - Adafruit_MAX31865, Adafruit_ICM20948, Adafruit_ICM20X, 
*/

#include "Ploughmeter.h"
#include <Wire.h>

// ————— DEEP SLEEP —————————————————————————————
#define TIME_TO_SLEEP 5 // Time to sleep in seconds

Ploughmeter ploughmeter;

void setup() 
{
  // Start wire communication
  Wire.begin();

  // Start serial communication at a speed of 115200 baud.
  Serial.begin(115200);

  /* Initialisation */
  ploughmeter.init();

  /* Get temperature sensor data */
  ploughmeter.getMAX31865();

  /* Get IMU data */
  ploughmeter.getICM20948();

  /* Get abs pressure sensor data */
  ploughmeter.getPAA20D();

  /* Get strain gages data */
  ploughmeter.getNAU7802();

  /* debug */
  ploughmeter.display();

  /* Deep sleep mode */
  ploughmeter.sleep(TIME_TO_SLEEP);
}

void loop() 
{
}


