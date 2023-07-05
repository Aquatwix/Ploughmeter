/*
  Project Name: Ploughmeter
  Description: Data acquisition from ploughmeter sensors and RF transmission at 169MHz.
  Author: Dorian Poissonnet
  Github: https://github.com/Aquatwix/Ploughmeter
  Created: 2023, May 30
  Version: v2.0

  Required Hardware: 
  - Feather Huzzah ESP8266
  - MAX31865 + PT100
  - SCL3300
  - ICM20948
  - PAA-20D x2
  - PAA-9LD
  - PD-10LX
  - NAU7802 + Strain gages

  Used Libraries
  - Wire.h
  - Adafruit_MAX31865.h                             
  - Adafruit_ICM20948.h
  - Adafruit_ICM20X.h
  - SCL3300.h
  - SparkFun_Qwiic_Scale_NAU7802_Arduino_Library.h
  - KellerLD.h   
  - PD10LX.h (Github: https://github.com/Aquatwix/PD-10LX-Library)
  - ESP8266WiFi.h
  - TCA9548A.h
  - SoftwareSerial.h
*/

#include "Ploughmeter.h"

Ploughmeter ploughmeter;
SoftwareSerial rfSerial(RX_PIN, TX_PIN);

void setup() 
{
  // Start wire communication
  Wire.begin();

  Serial.begin(115200);     // Start serial communication at a speed of 115200 baud.
  rfSerial.begin(19200);    // Start RF communication at a baud rate of 19200.
  delay(2700);              // Add a delay to allow time for the RF module to initialize properly. (min: 2700)

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


