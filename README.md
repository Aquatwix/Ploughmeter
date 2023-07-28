# Ploughmeter
Ploughmeter is an Arduino library designed for the Ploughmeter prototype. It enables data acquisition from various sensors used in the ploughmeter and facilitates RF transmission at 169MHz.

The Ploughmeter prototype is a device used for measuring and analyzing data related to ploughing operations. It integrates multiple sensors to gather information such as temperature, pressure, tilt, and more. The collected data can be transmitted wirelessly using the integrated radio frequency (RF) module.

# Overview

<img src="https://cdn.discordapp.com/attachments/993554363232559104/1126141322378625024/image.png"/>
<img src="https://cdn.discordapp.com/attachments/993554363232559104/1126141531330457630/image.png"/>
<img src="https://cdn.discordapp.com/attachments/993554363232559104/1126141713883344936/image.png"/>

# Requirements

## Hardware 
  - <a href="https://handsontec.com/dataspecs/module/esp8266-V13.pdf">Feather Huzzah ESP8266</a>
  - <a href="https://www.analog.com/media/en/technical-documentation/data-sheets/MAX31865.pdf">MAX31865</a> + <a href="https://www.micros.com.pl/mediaserver/info-cz%20pt100-4x32b%20iii%20ceramic.pdf">PT100</a>
  - <a href="https://www.murata.com/~/media/webrenewal/products/sensor/pdf/datasheet/datasheet_scl3300-d01.ashx?la=en-us">SCL3300</a>
  - <a href="https://invensense.tdk.com/wp-content/uploads/2016/06/DS-000189-ICM-20948-v1.3.pdf">ICM20948</a>
  - <a href="https://keller-druck.com/en/products/pressure-transducers/oem-pressure-transducers-with-thread/series-20">PAA-20D x2</a>
  - <a href="https://keller-druck.com/en/products/pressure-transmitters/oem-pressure-transmitters/series-9ld">PAA-9LD</a>
  - <a href="https://www.kelleramerica.com/file-cache/website_component/5e6a3b8f312d062dea25213d/datasheets/1586354957535">PD-10LX</a>
  - <a href="https://www.nuvoton.com/resource-files/NAU7802%20Data%20Sheet%20V1.7.pdf">NAU7802</a> + <a href="https://www.farnell.com/datasheets/3576189.pdf">Strain gages</a> + Wheatstone
  - <a href="https://www.ti.com/lit/ds/symlink/tca9548a.pdf?ts=1683781856694&ref_url=https%253A%252F%252Fwww.google.com%252F">TCA9548A</a>

## Software 
- Arduino IDE
- Python
- Radiocrafts tools (MBUS-DEMO & MBUS-CCT)

  ### Librairies
    - <a href="http://arduino.esp8266.com/stable/package_esp8266com_index.json">Feather Huzzah ESP8266</a>
    - <a href="https://github.com/adafruit/Adafruit_MAX31865">MAX31865</a> + PT100
    - <a href="https://github.com/DavidArmstrong/SCL3300">SCL3300</a>
    - <a href="https://github.com/adafruit/Adafruit_ICM20X/tree/master">ICM20948</a>
    - <a href="https://drive.google.com/drive/folders/101NB1hk6-6I5mgdBa2VgDFpXMAQXd578?usp=sharing">PAA-20D x2</a> ( = <a href="https://github.com/bluerobotics/BlueRobotics_KellerLD_Library">BlueRobotics Library</a> + local declaration of T)
    - <a href="https://drive.google.com/drive/folders/101NB1hk6-6I5mgdBa2VgDFpXMAQXd578?usp=sharing">PAA-9LD</a> ( = <a href="https://github.com/bluerobotics/BlueRobotics_KellerLD_Library">BlueRobotics Library</a> + local declaration of T)
    - <a href="https://github.com/Aquatwix/PD-10LX-Library/tree/main">PD-10LX</a>
    - <a href="https://github.com/sparkfun/SparkFun_Qwiic_Scale_NAU7802_Arduino_Library">NAU7802</a> + Strain gages + Wheatstone
    - <a href="https://github.com/WifWaf/TCA9548A">TCA9548A</a>
 
# Installation

## Step 1: Install the ESP8266 package and use the Adafruit Feather HUZZAH ESP8266 board.
- Refer to the Software section to obtain the json link for the ESP8266 package. Copy the link and insert it into Arduino IDE: (Arduino IDE > File > Preferences > Additionnal boards URL > paste json link)
- Install ESP8266 boards: (Arduino IDE > Tools > Board > Boards Manager > Search "esp8266" and install the package)
- Use the appropriate board: (Arduino IDE > Tools > Board > esp8266 > Adafruit Feather HUZZAH ESP8266)

## Step 2: Install all sensor libraries
- Refer to the Software section for the names of the sensor libraries. You can install them using the Arduino IDE search: (Arduino IDE > Tools > Manage Librairies > Search the names of librairies).
- The only exception is the PD-10LX library. To install it, download the library from the Github link and place the zip archive in the "Library" folder of your Arduino IDE installation. If successful, you'll be able to see the PD-10LX example: (Arduino IDE > File > Examples > PD-10LX-Library)
  
## Step 3: Download the Ploughmeter library
- Following the same principle as the PD-10LX library, download the Ploughmeter library and insert the archive in the "Library" folder of your Arduino IDE installation.
  
## Step 4 : Configure Radiocrafts modems and plug them on the board
To use the radio frequency protocol correctly, you need to configure correctly the transmitter and receiver modems.

<b>Warning</b> : to access the modems' registers, jumpers must be placed on the RX/TX pins.

<img src="https://cdn.discordapp.com/attachments/993554363232559104/1126162055091736576/image.png" height="250" width="250"/>

### Transmitter modem (left)
- Open the MBUS-CCT tool to configure your modem. Select the COM port and press the "Connect" button, then press the "Enter configuration mode" button and finally the "Load configuration" button to access the registers.
- You can use the same configuration as below. The most important thing is to set the network role to 1 (master) and the RSSI mode to 1 (active).

### Receiver modem (right)
- Open the MBUS-CCT tool to configure your modem. Select the COM port and press the "Connect" button, then press the "Enter configuration mode" button and finally the "Load configuration" button to access the registers.
- You can use the same configuration as below. The most important thing is to set the network role to 0 (slave).
- Don't forget to memorize the value of your control field. It serves as an identifier for sending data to the right modem.  

<img src="https://cdn.discordapp.com/attachments/993554363232559104/1126155357950062712/image.png"/>

Both modems must have the same RF channel, RF data rate, MBUS mode, A-field VER and A-field DEV.

## Step 5: Download the Ploughmeter example onto the board
- To open the Ploughmeter example: (Arduino IDE > File > Examples > Ploughmeter-Library > Ploughmeter_example)
- You can modify the sleep time by changing the TIME_TO_SLEEP variable.

## Step 6 : Modems installation

### Transmitter modem
The transmitter modem will send the data supplied by the microcontroller. 
- You must remove the RX/TX jumpers used for configuration.
- Connect the modem's RX pin to the ESP8266's TX pin.
- Move the power supply jumper to release the 3.3V pin.
- Connect the modem's 3,3V pin to the ESP8266's 3,3V pin.
- Don't forget to connect the grounds.

<img src="https://media.discordapp.net/attachments/993554363232559104/1131867365936730112/image.png" width="60%" heigth="60%"/>

### Receiver modem
- The receiving modem just needs to be connected to the computer. This means that the jumpers still need to be installed.

## Step 7: Data collection with the MBUS-DEMO tool
If the previous steps have gone smoothly, you're ready to retrieve the datas. You can see the orange LED blinking on the sending modem, indicating that data is being sent. The orange LED on the receiving modem should be blinking to indicate that data is being received.
- Open the MBUS-DEMO tool and select the COM port of your receiving modem.
- Go to the MBUS Packet Sniffer tool and press the "Start" button. You should see the dataframes arrive.
<img src="https://cdn.discordapp.com/attachments/993554363232559104/1126157504041189477/image.png"/>

## Step 8: Place them in the dataframe.txt file
This version is a prototype and the link with the data logger has not been created. You need to load the dataframes "by hand" if you want to analyze them.
- Copy "Data field", "RSSI" and "Timestamp" and paste the result into the decoder's dataframe.txt file.
<img src="https://cdn.discordapp.com/attachments/993554363232559104/1126159131712159854/image.png"/>
<img src="https://cdn.discordapp.com/attachments/993554363232559104/1126159476685295636/image.png"/>

## Step 9: Run main.py from the Decoder folder to analyze sensor data
Your dataframes are loaded. At this point, you're almost ready to analyze the sensor data.
If you decided to use a control field other than 0x08 in step 4, you need to modify it in the main.py file by changing the value of the "Ploughmeter_CI" variable to the correct one.
Now you can analyze the sensor data by running the decoder's main.py file.
<img src="https://cdn.discordapp.com/attachments/993554363232559104/1126159992156856380/image.png"/>
