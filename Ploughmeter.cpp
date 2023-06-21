#include "Ploughmeter.h"

/**
 * @name Ploughmeter()
*/
Ploughmeter::Ploughmeter() : MAX31865(CS_MAX31865_PIN)
{
    //
}

/**
 * @name init()
*/
void Ploughmeter::init() 
{  
    // —————————————————— SPI ——————————————————
    // Initialisation of the SCL3300 sensor
    this->state_SCL3300 = this->_SCL3300.begin(CS_SCL3300_PIN);
    
    // Initialisation of the MAX31865 sensor
    this->state_MAX31865 = this->MAX31865.begin(MAX31865_4WIRE);

    // —————————————————— I2C ——————————————————
    // Initialisation of the PD-10LX sensor [I2C-0]
    this->selectI2Cbus(TCA9548A_BUS_PD10LX);
    this->state_PD10LX = this->PD10LX_.init();

    // Initialisation of the ICM20948 sensor [I2C-1]
    this->selectI2Cbus(TCA9548A_BUS_ICM20948);
    this->ICM20948.setAccelRange(ICM20948_ACCEL_RANGE_2_G); 
    this->state_ICM20948 = this->ICM20948.begin_I2C(ICM20948_ADDR);

    // Initialisation of the PAA-20D (1) sensor [I2C-2]
    this->selectI2Cbus(TCA9548A_BUS_PAA20D_1);
    this->PAA20D_1.init();                                   
    this->PAA20D_1.setFluidDensity(997);
    this->state_PAA20D_1 = this->PAA20D_1.isInitialized();

    // Initialisation of the PAA-20D (2) sensor [I2C-3]
    this->selectI2Cbus(TCA9548A_BUS_PAA20D_2);
    this->PAA20D_2.init();                                   
    this->PAA20D_2.setFluidDensity(997);
    this->state_PAA20D_2 = this->PAA20D_2.isInitialized();

    // Initialisation of the PAA-9LD sensor [I2C-4]
    this->selectI2Cbus(TCA9548A_BUS_PAA9LD);
    this->PAA9LD.init();                                   
    this->PAA9LD.setFluidDensity(997);
    this->state_PAA9LD = this->PAA9LD.isInitialized();

    // Initialisation of the NAU7802 sensor [I2C-5]
    this->selectI2Cbus(TCA9548A_BUS_NAU7802);
    this->state_NAU7802 = this->_NAU7802.begin();
    this->_NAU7802.clearBit(NAU7802_PGA_PWR_PGA_CAP_EN, NAU7802_PGA_PWR); //Disable 330pF decoupling on chan 2 (cut the trace)
    this->_NAU7802.setLDO(NAU7802_LDO_3V0); //Set the onboard Low - Drop - Out voltage regulator to a given value
    this->_NAU7802.setSampleRate(NAU7802_SPS_80); //Sample rate can be set to 10, 20, 40, 80, or 320Hz
    this->_NAU7802.setGain(NAU7802_GAIN_2); //Gain can be set to 1, 2, 4, 8, 16, 32, 64, or 128.
}

/**
 * @name getMAX31865()
*/
void Ploughmeter::getMAX31865() 
{
    if(this->state_MAX31865 && this->MAX31865.readRTD()) // vérifier la valeur du rtd, pas moyen de vérifier depuis ma fonction begin de ce capteur
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
        this->selectI2Cbus(TCA9548A_BUS_ICM20948);
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
 * @name getPAA20D_1()
*/
void Ploughmeter::getPAA20D_1()
{                                       
    if(this->state_PAA20D_1)                     
    {                       
        this->selectI2Cbus(TCA9548A_BUS_PAA20D_1);           
        this->PAA20D_1.read();

        // Dave datas in array
        this->PAA20D_1_pressure = this->PAA20D_1.pressure();
        this->PAA20D_1_temp = this->PAA20D_1.temperature();                 
    }                                                
    else                                            
    {              
        Serial.println("Error : PAA-20D (1) is not detected");                                                 
        this->state_PAA20D_1 = false;                                          
    } 
}

/**
 * @name getPAA20D_2()
*/
void Ploughmeter::getPAA20D_2()
{                                       
    if(this->state_PAA20D_2)                     
    {                       
        this->selectI2Cbus(TCA9548A_BUS_PAA20D_2);           
        this->PAA20D_2.read();

        // Dave datas in array
        this->PAA20D_2_pressure = this->PAA20D_2.pressure();
        this->PAA20D_2_temp = this->PAA20D_2.temperature();                 
    }                                                
    else                                            
    {              
        Serial.println("Error : PAA-20D (2) is not detected");                                                 
        this->state_PAA20D_2 = false;                                          
    } 
}

/**
 * @name getPD10LX()
*/
void Ploughmeter::getPD10LX()
{                                       
    if(this->state_PD10LX)                     
    {                       
        this->selectI2Cbus(TCA9548A_BUS_PD10LX);   
        this->PD10LX_.read();        
        this->PD10LX_pressure = this->PD10LX_.getPressure(); 
        this->PD10LX_temp = this->PD10LX_.getTemperature();        
    }                                                
    else                                            
    {              
        Serial.println("Error : PD-10LX is not detected");                                                 
        this->state_PD10LX = false;                                          
    } 
}

/**
 * @name getPAA9LD()
*/
void Ploughmeter::getPAA9LD()
{                                       
    if(this->state_PAA9LD)                     
    {                       
        this->selectI2Cbus(TCA9548A_BUS_PAA9LD);   
        this->PAA9LD.read();

        // Dave datas in array
        this->PAA9LD_pressure = this->PAA9LD.pressure();
        this->PAA9LD_temp = this->PAA9LD.temperature();      
    }                                                
    else                                            
    {              
        Serial.println("Error : PAA-9LD is not detected");                                                 
        this->state_PAA9LD = false;                                          
    } 
}

/**
 * @name getNAU7802()
*/
void Ploughmeter::getNAU7802()
{
    if(this->state_NAU7802)                     
    {                     
        this->selectI2Cbus(TCA9548A_BUS_NAU7802);
        this->_NAU7802.setChannel(NAU7802_CHANNEL_1);
        delay(100); //Delay needed after channel change
        this->_NAU7802.calibrateAFE(); //Does an internal calibration. Recommended after power up, gain changes, sample rate changes, or channel changes.
        delay(100); //Delay needed after calibrateAFE
        if (this->_NAU7802.available() == true)
        {
            this->ploughX = this->_NAU7802.getAverage(20);
        }

        this->_NAU7802.setChannel(NAU7802_CHANNEL_2);
        delay(100); //Delay needed after channel change
        this->_NAU7802.calibrateAFE(); //Does an internal calibration. Recommended after power up, gain changes, sample rate changes, or channel changes.
        delay(100); //Delay needed after calibrateAFE
        if (this->_NAU7802.available() == true)
        {
            this->ploughY = this->_NAU7802.getAverage(20);
        }
    }                                                
    else                                            
    {              
        Serial.println("Error : NAU7802 is not detected");                                                 
        this->state_NAU7802 = false;                                          
    } 
}

/**
 * @name getSCL3300()
*/
void Ploughmeter::getSCL3300()
{
    if(this->state_SCL3300)                     
    {  
        this->tiltX = -90;
        this->tiltY = -90;

        if (this->_SCL3300.available()) { //Get next block of data from sensor
            this->tiltX = this->_SCL3300.getTiltLevelOffsetAngleX();
            this->tiltY = this->_SCL3300.getTiltLevelOffsetAngleY();
        }
        // uint16_t tiltX_Int = tiltX * 100 + 18000;
        // uint16_t tiltY_Int = tiltY * 100 + 18000;
    }                                                
    else                                            
    {              
        Serial.println("Error : SCL3300 is not detected");                                                 
        this->state_SCL3300 = false;                                          
    } 
}


/**
 * @name sendSensorData()
*/
void Ploughmeter::sendSensorData(SoftwareSerial& ss)
{
    uint8_t packet[4];
    packet[0] = sizeof(packet) - 1;         // Nombre d'octets à envoyer
    packet[1] = 0x08;                       // CI

    packet[2] = this->PD10LX_pressure;    
    packet[3] = this->PD10LX_temp;                       
    ss.write(packet, sizeof(packet));
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

    if(this->state_SCL3300)
    {
        Serial.println("\n——————— SCL3300 ———————");
        Serial.print("Tilt X:\t"); Serial.println(this->tiltX);
        Serial.print("Tilt Y:\t"); Serial.println(this->tiltY);
    }  

    if(this->state_ICM20948)
    {
        Serial.println("\n——————— ICM20948 ———————");
        Serial.print("Roll:\t"); Serial.println(this->roll); 
        Serial.print("Pitch:\t"); Serial.println(this->pitch);
        Serial.print("Yaw:\t"); Serial.println(this->yaw);
    }

    if(this->state_PAA20D_1)
    {
        Serial.println("\n——————— PAA-20D (1) ———————");
        Serial.print("Pressure:\t"); Serial.println(this->PAA20D_1_pressure); 
        Serial.print("Temperature:\t"); Serial.println(this->PAA20D_1_temp);
    }

    if(this->state_PAA20D_2)
    {
        Serial.println("\n——————— PAA-20D (2) ———————");
        Serial.print("Pressure:\t"); Serial.println(this->PAA20D_2_pressure); 
        Serial.print("Temperature:\t"); Serial.println(this->PAA20D_2_temp);
    }

    if(this->state_PAA9LD)
    {
        Serial.println("\n——————— PAA-9LD ———————");
        Serial.print("Pressure:\t"); Serial.println(this->PAA9LD_pressure); 
        Serial.print("Temperature:\t"); Serial.println(this->PAA9LD_temp);
    }

    if(this->state_PD10LX)
    {
        Serial.println("\n——————— PD-10LX ———————");
        Serial.print("Pressure:\t"); Serial.println(this->PD10LX_pressure); 
        Serial.print("Temperature:\t"); Serial.println(this->PD10LX_temp);
    }

    if(this->state_NAU7802)
    {
        Serial.println("\n——————— NAU7802 ———————");
        Serial.print("PloughX:\t"); Serial.println(this->ploughX); 
        Serial.print("PloughY:\t"); Serial.println(this->ploughY); 
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

/**
 *
*/
void Ploughmeter::selectI2Cbus(uint8_t bus)
{
  Wire.beginTransmission(TCA9548A_DEFAULT);  // TCA9548A address
  Wire.write(1 << bus);          // send byte to select bus
  Wire.endTransmission();
}