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

// ————— DEEP SLEEP —————————————————————————————
#define TIME_TO_SLEEP 0.5 // Time to sleep in seconds

Ploughmeter ploughmeter;
SoftwareSerial rfSerial(RX_PIN, TX_PIN);

void setup() 
{
  // Start wire communication
  Wire.begin();

  Serial.begin(115200);     // Start serial communication at a speed of 115200 baud.
  rfSerial.begin(19200);  // Start RF communication at a baud rate of 19200.
  delay(2700); // Add a delay to allow time for the RF module to initialize properly.

  /* Initialisation */
  ploughmeter.init();

  /* Get temperature sensor data */
  ploughmeter.getMAX31865();

  /* Get tilt from inclinometer  */
  ploughmeter.getSCL3300();

  /* Get IMU data */
  ploughmeter.getICM20948();

  /* Get abs pressure sensor data */
  ploughmeter.getPAA20D_1();

  /* Get abs pressure sensor data */
  ploughmeter.getPAA20D_2();

  /* Get pressure sensor data */
  ploughmeter.getPAA9LD();

  /* Get diff pressure sensor data */
  ploughmeter.getPD10LX();

  /* Get strain gages data */
  ploughmeter.getNAU7802();

  /* Send data through RF */
  ploughmeter.sendSensorData(rfSerial);

  /* debug */
  ploughmeter.display();

  /* Deep sleep mode */
  ploughmeter.sleep(TIME_TO_SLEEP);
}

void loop() 
{
}


