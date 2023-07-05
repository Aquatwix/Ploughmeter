import math
import os
from datetime import datetime
import matplotlib.pyplot as plt

# @brief Verifies the integrity of data using CRC-16 checksum.
# @name verify_crc16
# @params
# - data: The data to be checked for integrity. Should be a bytearray or a sequence of bytes.
# - received_crc: The received CRC-16 value to compare with the calculated CRC-16.
# @return True if the calculated CRC-16 matches the received CRC-16, False otherwise.
def verify_crc16(data, received_crc):

    crc = 0xFFFF

    # Iterate over each byte in the data
    for byte in data:
        crc ^= byte << 8

        # Perform bitwise XOR and bit shifting
        for _ in range(8):
            if crc & 0x8000:
                crc = (crc << 1) ^ 0x1021
            else:
                crc <<= 1

    # Check if the calculated CRC-16 matches the received CRC-16
    return crc & 0xFFFF == received_crc


# @brief: Converts the resistance of an RTD sensor to temperature using the Callendar-Van Dusen equation.
# @name: RTD_to_temp
# @params:
# - RTDraw: The resistance value of the RTD sensor in Ohms.
# @return: The temperature value in degrees Celsius calculated based on the RTD resistance.
def RTD_to_temp(RTDraw):

    RTD_A = 3.9083e-3
    RTD_B = -5.775e-7
    RTDnominal = 100
    refResistor = 430
    Z1, Z2, Z3, Z4, Rt, temp = 0.0, 0.0, 0.0, 0.0, 0.0, 0.0

    Rt = RTDraw
    Rt /= 32768
    Rt *= refResistor

    Z1 = -RTD_A
    Z2 = RTD_A * RTD_A - (4 * RTD_B)
    Z3 = (4 * RTD_B) / RTDnominal
    Z4 = 2 * RTD_B

    temp = Z2 + (Z3 * Rt)
    temp = (math.sqrt(temp) + Z1) / Z4

    if temp >= 0:
        return temp

    Rt /= RTDnominal
    Rt *= 100  # normalize to 100 ohm
    rpoly = Rt

    temp = -242.02
    temp += 2.2228 * rpoly
    rpoly *= Rt  # square
    temp += 2.5859e-3 * rpoly
    rpoly *= Rt  # ^3
    temp -= 4.8260e-6 * rpoly
    rpoly *= Rt  # ^4
    temp -= 2.8183e-8 * rpoly
    rpoly *= Rt  # ^5
    temp += 1.5243e-10 * rpoly

    return temp



# @brief Reads data from a file and extracts datas, rssis, and times lists.
# @name readDataframe
# @params:
# - filename: The name of the file to read.
# @return A tuple containing the datas list, times list, and rssis list.
def readDataframe(filename):

    # Construct the file path
    path = os.getcwd() + '/decoder/' + filename

    datas, rssis, times = [], [], []

    try:
        # Open the file for reading
        with open(path, 'r') as file:
            lines = file.readlines()

            # Iterate over each line in the file
            for line in lines:
                # Split the line into data, rssi, and time values
                data, rssi, time = line.strip().split('	')

                # Append the values to their respective lists
                datas.append(data)
                rssis.append(rssi)
                times.append(time)

    except:
        print(f"Error: the specified file was not found in {path}")

    # Return the extracted lists as a tuple
    return datas, times


# @brief Plots sensor data over time.
# @name plotData
# @params
# - sensor_datas: A list of tuples containing sensor data and timestamps.
# - title: The title of the plot.
# - labely: The label for the y-axis.
def plotData(sensor_datas, title, labely):

    timestamps = [datetime.strptime(paire[1], '%d.%m.%Y %H:%M:%S') for paire in sensor_datas]
    datas = [paire[0] for paire in sensor_datas]

    # Create the plot
    plt.plot(timestamps, datas, linestyle='-', color='blue')

    # Add labels and titles
    plt.xlabel("Date")
    plt.ylabel(labely)
    plt.title(title)

    # Format timestamps on the x-axis
    plt.xticks(rotation=45)

    # Display the plot
    plt.tight_layout()
    plt.show()


# @brief Plots MAX31865 temperature data over time.
# @name plotMAX31865Data
# @params
# - temperatures: A list of tuples containing temperature data and timestamps.
def plotMAX31865Data(temperatures):

    timestamps = [datetime.strptime(paire[1], '%d.%m.%Y %H:%M:%S') for paire in temperatures]
    datas = [paire[0] for paire in temperatures]

    # Create the plot for MAX31865
    plt.subplot(2, 4, 1)
    plt.plot(timestamps, datas, linestyle='-', color='blue')
    plt.xlabel("Date")
    plt.ylabel("Temperature (°C)")
    plt.title("MAX31865")
    plt.xticks(rotation=45)


# @brief Plots SCL3300 tilt data over time.
# @name plotSCL3300Data
# @params
# - tilts: A list of tuples containing tilt data, timestamps, and axis labels.
def plotSCL3300Data(tilts):

    timestamps = [datetime.strptime(paire[2], '%d.%m.%Y %H:%M:%S') for paire in tilts]
    tiltX = [paire[0] for paire in tilts]
    tiltY = [paire[1] for paire in tilts]

    # Create the plot for SCL3300
    plt.subplot(2, 4, 2)
    plt.plot(timestamps, tiltX, linestyle='-', color='blue', label='TiltX')
    plt.plot(timestamps, tiltY, linestyle='-', color='red', label='TiltY')
    plt.xlabel("Date")
    plt.ylabel("Angle (°)")
    plt.title("SCL3300")
    plt.xticks(rotation=45)
    plt.legend()


# @brief Plots ICM20948 angle data over time.
# @name plotICM20948Data
# @params
# - angles: A list of tuples containing angle data, timestamps, and axis labels.
def plotICM20948Data(angles):

    timestamps = [datetime.strptime(paire[3], '%d.%m.%Y %H:%M:%S') for paire in angles]
    roll = [paire[0] for paire in angles]
    pitch = [paire[1] for paire in angles]
    yaw = [paire[2] for paire in angles]

    # Create the plot for ICM20948
    plt.subplot(2, 4, 3)
    plt.plot(timestamps, roll, linestyle='-', color='blue', label='Roll')
    plt.plot(timestamps, pitch, linestyle='-', color='red', label='Pitch')
    plt.plot(timestamps, yaw, linestyle='-', color='green', label='Yaw')
    plt.xlabel("Date")
    plt.ylabel("Angle (°)")
    plt.title("ICM20948")
    plt.xticks(rotation=45)
    plt.legend()


# @brief Plots PAA20D1 sensor data over time.
# @name plotPAA20D1Data
# @params
# - datas: A list of tuples containing PAA20D1 sensor data, timestamps, and axis labels.
def plotPAA20D1Data(datas):

    timestamps = [datetime.strptime(paire[2], '%d.%m.%Y %H:%M:%S') for paire in datas]
    p = [paire[0] for paire in datas]
    t = [paire[1] for paire in datas]

    # Create the plot for PAA20D1
    plt.subplot(2, 4, 4)
    plt.plot(timestamps, p, linestyle='-', color='blue', label='Pressure')
    plt.plot(timestamps, t, linestyle='-', color='red', label='Temperature')
    plt.xlabel("Date")
    plt.ylabel("Bar and °C")
    plt.title("PAA-20D 1")
    plt.xticks(rotation=45)
    plt.legend()


# @brief Plots PAA20D2 sensor data over time.
# @name plotPAA20D2Data
# @params
# - datas: A list of tuples containing PAA20D2 sensor data, timestamps, and axis labels.
def plotPAA20D2Data(datas):

    timestamps = [datetime.strptime(paire[2], '%d.%m.%Y %H:%M:%S') for paire in datas]
    p = [paire[0] for paire in datas]
    t = [paire[1] for paire in datas]

    # Create the plot for PAA20D2
    plt.subplot(2, 4, 5)
    plt.plot(timestamps, p, linestyle='-', color='blue', label='Pressure')
    plt.plot(timestamps, t, linestyle='-', color='red', label='Temperature')
    plt.xlabel("Date")
    plt.ylabel("Bar and °C")
    plt.title("PAA-20D 2")
    plt.xticks(rotation=45)
    plt.legend()


# @brief Plots PAA9LD sensor data over time.
# @name plotPAA9LDData
# @params
# - datas: A list of tuples containing PAA9LD sensor data, timestamps, and axis labels.
def plotPAA9LDData(datas):

    timestamps = [datetime.strptime(paire[2], '%d.%m.%Y %H:%M:%S') for paire in datas]
    p = [paire[0] for paire in datas]
    t = [paire[1] for paire in datas]

    # Create the plot for PAA9LD
    plt.subplot(2, 4, 6)
    plt.plot(timestamps, p, linestyle='-', color='blue', label='Pressure')
    plt.plot(timestamps, t, linestyle='-', color='red', label='Temperature')
    plt.xlabel("Date")
    plt.ylabel("Bar and °C")
    plt.title("PAA-9LD")
    plt.xticks(rotation=45)
    plt.legend()


# @brief Plots PD10LX sensor data over time.
# @name plotPD10LXData
# @params
# - datas: A list of tuples containing PD10LX sensor data, timestamps, and axis labels.
def plotPD10LXData(datas):

    timestamps = [datetime.strptime(paire[2], '%d.%m.%Y %H:%M:%S') for paire in datas]
    p = [paire[0] for paire in datas]
    t = [paire[1] for paire in datas]

    # Create the plot for PD10LX
    plt.subplot(2, 4, 7)
    plt.plot(timestamps, p, linestyle='-', color='blue', label='Pressure')
    plt.plot(timestamps, t, linestyle='-', color='red', label='Temperature')
    plt.xlabel("Date")
    plt.ylabel("Bar and °C")
    plt.title("PD-10LX")
    plt.xticks(rotation=45)
    plt.legend()


# @brief Plots NAU7802 sensor data over time.
# @name plotNAU7802Data
# @params
# - datas: A list of tuples containing NAU7802 sensor data, timestamps, and axis labels.
def plotNAU7802Data(datas):

    timestamps = [datetime.strptime(paire[2], '%d.%m.%Y %H:%M:%S') for paire in datas]
    ploughX = [paire[0] for paire in datas]
    ploughY = [paire[1] for paire in datas]

    # Create the plot for NAU7802
    plt.subplot(2, 4, 8)
    plt.plot(timestamps, ploughX, linestyle='-', color='blue', label='PloughX')
    plt.plot(timestamps, ploughY, linestyle='-', color='red', label='PloughY')
    plt.xlabel("Date")
    plt.ylabel("Value")
    plt.title("NAU7802")
    plt.xticks(rotation=45)
    plt.legend()