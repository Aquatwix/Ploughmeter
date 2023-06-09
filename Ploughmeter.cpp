#include "Ploughmeter.h"

/**
 * @name Ploughmeter()
*/
Ploughmeter::Ploughmeter() : MAX31865(CS_PIN, MOSI_PIN, MISO_PIN, SCK_PIN)
{
    //
}

/**
 * @name init()
*/
void Ploughmeter::init() 
{  
    // Initialisation of the MAX31865 sensor
    this->state_MAX31865 = this->MAX31865.begin(MAX31865_4WIRE) && !MAX31865.readFault();

    // Initialisation of the ICM20948 sensor
    this->ICM20948.setAccelRange(ICM20948_ACCEL_RANGE_2_G); 
    this->state_ICM20948 = this->ICM20948.begin_I2C(ICM20948_ADDR);

    // Initialisation of the PAA-20D sensor
    this->PAA20D.init();                                   
    this->PAA20D.setFluidDensity(997);
    this->state_PAA20D = this->PAA20D.isInitialized();

    // Initialisation of the NAU7802 sensor
    this->NAU7802.begin();
    this->NAU7802.setLDO(NAU7802_3V0);
    this->NAU7802.setGain(NAU7802_GAIN_128);
    this->NAU7802.setRate(NAU7802_RATE_10SPS);
    // Take 10 readings to flush out readings
    for (uint8_t i=0; i<10; i++) {
        while (! this->NAU7802.available()) delay(1);
        this->NAU7802.read();
    }
    this->NAU7802.calibrate(NAU7802_CALMOD_INTERNAL);
    this->NAU7802.calibrate(NAU7802_CALMOD_OFFSET);
    this->state_NAU7802 = !this->NAU7802.available();
}

/**
 * @name getMAX31865()
*/
void Ploughmeter::getMAX31865() 
{
    if(this->state_MAX31865)
    {
        this->MAX31865_rtd = this->MAX31865.readRTD();                 // RTD
        this->MAX31865_ratio = this->MAX31865_rtd / 32768;           // Ratio
        this->MAX31865_resistance = this->MAX31865_ratio * RREF;     // Resistance
        this->MAX31865_temp = MAX31865.temperature(RNOMINAL, RREF);    // Temperature
    }
    else
    {
        Serial.println("Error : MAX31865 is not detected");
        this->state_MAX31865 = false;
    }
}

/**
 * @name getICM20948()
*/
void Ploughmeter::getICM20948()
{
    if(this->state_ICM20948) 
    {                                       
        // Storage for accelerometer and magnetometer
        sensors_event_t accel;
        sensors_event_t mag;

        // Get accelerometer and magnetometer
        Adafruit_Sensor *icm_accel, *icm_gyro, *icm_mag;
        icm_accel = this->ICM20948.getAccelerometerSensor();  
        icm_mag = this->ICM20948.getMagnetometerSensor(); 
        icm_accel->getEvent(&accel);
        icm_mag->getEvent(&mag);

        // Get roll, pitch and yaw angles in degrees
        this->roll  = 180 / PI * atan2(accel.acceleration.y, accel.acceleration.z);                                        // positive is left wing up
        this->pitch = 180 / PI * atan2(accel.acceleration.x, sqrt(accel.acceleration.y * accel.acceleration.y + accel.acceleration.z * accel.acceleration.z)); // positive is nose up
        this->yaw   = 180 / PI * atan2(mag.magnetic.y * cos(roll) + mag.magnetic.z * sin(roll), mag.magnetic.x * cos(pitch) + mag.magnetic.y * sin(pitch) * sin(roll) + mag.magnetic.z * sin(pitch) * cos(roll)); // positive is nose right          
    }
    else
    {
        Serial.println("Error : ICM20948 is not detected");
        this->state_ICM20948 = false;
    }
}

/**
 * @name getPAA20D()
*/
void Ploughmeter::getPAA20D()
{                                       
    if(this->state_PAA20D)                     
    {                                                
        this->PAA20D.read();

        // Dave datas in array
        this->PAA20D_pressure = this->PAA20D.pressure();
        this->PAA20D_temp = this->PAA20D.temperature();                 
    }                                                
    else                                            
    {              
        Serial.println("Error : PAA-20D is not detected");                                                 
        this->state_PAA20D = false;                                          
    } 
}

/**
 * @name getNAU7802()
*/
void Ploughmeter::getNAU7802()
{
    if(this->state_NAU7802)                     
    {                     
        // Take 10 readings to flush out readings
        for (uint8_t i=0; i<10; i++) {
          while (!this->NAU7802.available()) delay(1);
          this->NAU7802.read();
        }                        
        this->ploughX = this->NAU7802.read();
    }                                                
    else                                            
    {              
        Serial.println("Error : NAU7802 is not detected");                                                 
        this->state_NAU7802 = false;                                          
    } 
}

/**
 * @name display()
*/
void Ploughmeter::display()
{
    if(this->state_MAX31865)
    {
        Serial.println("\n——————— MAX31865 ———————");
        Serial.print("RTD:\t"); Serial.println(this->MAX31865_rtd);
        Serial.print("Ratio:\t"); Serial.println(this->MAX31865_ratio);
        Serial.print("Resistance:\t"); Serial.println(this->MAX31865_resistance);
        Serial.print("Temperature:\t"); Serial.println(this->MAX31865_temp);
    }

    if(this->state_ICM20948)
    {
        Serial.println("\n——————— ICM20948 ———————");
        Serial.print("Roll:\t"); Serial.println(this->roll); 
        Serial.print("Pitch:\t"); Serial.println(this->pitch);
        Serial.print("Yaw:\t"); Serial.println(this->yaw);
    }

    if(this->state_PAA20D)
    {
        Serial.println("\n——————— PAA-20D ———————");
        Serial.print("Pressure:\t"); Serial.println(this->PAA20D_pressure); 
        Serial.print("Temperature:\t"); Serial.println(this->PAA20D_temp);
    }

    if(this->state_NAU7802)
    {
        Serial.println("\n——————— NAU7802 ———————");
        Serial.print("PloughX:\t"); Serial.println(this->ploughX); 
    }
}

/**
 * @name sleep()
*/
void Ploughmeter::sleep(float time_to_sleep)
{
    Serial.print("\nSleep for "); Serial.print(time_to_sleep); Serial.println(" second(s).\n"); 
    ESP.deepSleep(time_to_sleep * 1000000);
}