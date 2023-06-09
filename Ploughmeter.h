#ifndef PLOUGHMETER_H
#define PLOUGHMETER_H

#include "Arduino.h"

#include <Wire.h>                // I2C              
#include <Adafruit_MAX31865.h>   // MAX31865
#include <Adafruit_ICM20948.h>   // ICM20948
#include <Adafruit_ICM20X.h>     // ICM20948  
#include <SCL3300.h>             // SCL3300  
#include <Adafruit_NAU7802.h>    // NAU7802         
#include "KellerLD.h"            // PAA-20D 
#include <ESP8266WiFi.h>         

// ————— SPI ————————————————————————————————————
#define CS_PIN   0       // CS (Chip Select)          
#define MOSI_PIN 13      // MOSI (Master Out Slave In)
#define MISO_PIN 12      // MISO (Master In Slave Out)
#define SCK_PIN  14      // SCK (Serial Clock)   

// ————— MAX31865 ———————————————————————————————
#define RREF      430.0  // 430.0 for PT100       
#define RNOMINAL  100.0  // 100.0 for PT100    

// ————— ICM20948 ———————————————————————————————
#define ICM20948_ADDR 0x68 // 

class Ploughmeter 
{
  public:

    // Constructor for Ploughmeter class
    Ploughmeter();

    /** 
    * Initializes the registers of the PD10LX sensor
    */
    void init();

    /**
     * 
    */
    void getMAX31865();

    /**
     * 
    */
    void getICM20948();

    /**
     * 
    */
    void getPAA20D();

   /**
    * 
   */
    void getNAU7802();

    /**
     * 
    */
    void display();

    /**
    *
    */
    void sleep(float time);

  private:
    
    /**
     * Variables used for MAX31865 sensor
    */
    Adafruit_MAX31865 MAX31865;
    float MAX31865_rtd;
    float MAX31865_ratio;
    float MAX31865_resistance;
    float MAX31865_temp;
    bool state_MAX31865;

    /**
     * Variables used for ICM20948 sensor
    */
    Adafruit_ICM20948 ICM20948;                               
    float roll;
    float pitch;
    float yaw;
    bool state_ICM20948;    

    /**
     * Variables used for Keller PAA-20D sensor
    */
    KellerLD PAA20D;
    float PAA20D_pressure;
    float PAA20D_temp;
    bool state_PAA20D;   

    /**
     * 
    */     
    Adafruit_NAU7802 NAU7802;
    float ploughX;
    bool state_NAU7802;

};

#endif