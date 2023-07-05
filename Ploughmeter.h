#ifndef PLOUGHMETER_H
#define PLOUGHMETER_H

#include "Arduino.h"

#include <Wire.h>                                                 // I2C              
#include <Adafruit_MAX31865.h>                                    // MAX31865
#include <Adafruit_ICM20948.h>                                    // ICM20948
#include <Adafruit_ICM20X.h>                                      // ICM20948  
#include <SCL3300.h>                                              // SCL3300  
#include <SparkFun_Qwiic_Scale_NAU7802_Arduino_Library.h>         // NAU7802         
#include "KellerLD.h"                                             // PAA-20D 
#include <PD10LX.h>                                               // PD-10LX
#include <ESP8266WiFi.h>                                          // SleepMode
#include <TCA9548A.h>                                             // TCA9548A
#include <SoftwareSerial.h>                                       // RF

// —————— DEEP SLEEP —————————————————————————————
#define TIME_TO_SLEEP 1  // Time to sleep in seconds

// —————— RF ————————————————————————————————————
#define RX_PIN   3
#define TX_PIN   1

// ————— SPI ————————————————————————————————————
#define CS_MAX31865_PIN   15         
#define CS_SCL3300_PIN    0          

// ————— MAX31865 ———————————————————————————————
#define RREF      430.0  // 430.0 for PT100       
#define RNOMINAL  100.0  // 100.0 for PT100    

// ————— TCA9548A ————————————————————————————————
#define TCA9548A_DEFAULT 0x70
#define TCA9548A_BUS_PD10LX    0
#define TCA9548A_BUS_ICM20948  1
#define TCA9548A_BUS_PAA20D_1  2
#define TCA9548A_BUS_PAA20D_2  3
#define TCA9548A_BUS_PAA9LD    4
#define TCA9548A_BUS_NAU7802   5

// ————— ICM20948 ———————————————————————————————
#define ICM20948_ADDR 0x68 // 

class Ploughmeter 
{
  public:

    /* Constructor for Ploughmeter class */
    Ploughmeter();

    /**
     * @brief Initializes the sensors.
     * @name init
    */
    void init();

    /**
     * @brief Retrieves data from the MAX31865 sensor.
     * @name getMAX31865
    */
    void getMAX31865();

    /**
     * @brief Retrieves data from the ICM20948 sensor.
     * @name getICM20948
    */
    void getICM20948();

    /**
     * @brief Retrieves data from the PAA-20D (1) sensor.
     * @name getPAA20D_1
    */
    void getPAA20D_1();

    /**
     * @brief Retrieves data from the PAA-20D (2) sensor.
     * @name getPAA20D_2
    */
    void getPAA20D_2();

    /**
     * @brief Retrieves data from the PD-10LX sensor.
     * @name getPD10LX
    */
    void getPD10LX();

    /**
     * @brief Retrieves data from the PAA-9LD sensor.
     * @name getPAA9LD
    */
    void getPAA9LD();

    /**
     * @brief Retrieves data from the NAU7802 sensor.
     * @name getNAU7802
    */
    void getNAU7802();

    /**
     * @brief Retrieves data from the SCL3300 sensor.
     * @name getSCL3300
    */
    void getSCL3300();

    /**
     * @brief Displays the sensor data on the Serial Monitor.
     * @name display()
    */
    void display();

    /**
     * @brief Sends sensor data over a serial connection.
     * @name sendSensorData
     * @param ss The SoftwareSerial object for the serial rf connection.
    */
    void sendSensorData(SoftwareSerial &ss);

    /**
     * @brief Selects the I2C bus for communication.
     * @name selectI2Cbus()
     * @param bus The bus number to select.
    */
    void selectI2Cbus(uint8_t bus);

    /**
     * @brief Generates a CRC16 checksum for the given data.
     * @name generate_crc16()
     * @param data The data array to calculate the checksum for.
     * @param length The length of the data array.
     * @return The calculated CRC16 checksum.
    */
    uint16_t generate_crc16(uint8_t* data, size_t length);

    /**
     * @brief Puts the device into deep sleep mode for a specified duration.
     * @name sleep()
     * @param time_to_sleep The number of seconds to sleep.
    */
    void sleep(float time);

  private:
    
    /**
     * Variables used for MAX31865 sensor
    */
    Adafruit_MAX31865 MAX31865;
    int MAX31865_rtd;
    float MAX31865_ratio;
    float MAX31865_resistance;
    float MAX31865_temp;
    bool state_MAX31865 = false;

    /**
     * Variables used for ICM20948 sensor
    */
    Adafruit_ICM20948 ICM20948;                               
    float roll;
    float pitch;
    float yaw;
    bool state_ICM20948 = false;    

    /**
     * Variables used for Keller PAA-20D sensor (1)
    */
    KellerLD PAA20D_1;
    float PAA20D_1_pressure;
    float PAA20D_1_temp;
    bool state_PAA20D_1 = false;   

    /**
     * Variables used for Keller PAA-20D sensor (2)
    */
    KellerLD PAA20D_2;
    float PAA20D_2_pressure;
    float PAA20D_2_temp;
    bool state_PAA20D_2 = false;   

    /**
     * Variables used for Keller PD-10LXi sensor 
    */
    PD10LX PD10LX_;
    float PD10LX_pressure;
    float PD10LX_temp;
    bool state_PD10LX = false;  

    /**
     * Variables used for Keller PD-10LXi sensor 
    */
    KellerLD PAA9LD;
    float PAA9LD_pressure;
    float PAA9LD_temp;
    bool state_PAA9LD = false; 

    /**
     * Variables used for Keller NAU7802 sensor
    */     
    NAU7802 _NAU7802;
    uint32_t ploughX;
    uint32_t ploughY;
    bool state_NAU7802 = false;

    /**
     * Variables used for Keller SCL3300 sensor
    */
    SCL3300 _SCL3300;
    float tiltX;
    float tiltY;
    bool state_SCL3300 = false;
};

#endif