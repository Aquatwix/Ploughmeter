import math
import os
from datetime import datetime
import matplotlib.pyplot as plt

# @brief: Verifies the integrity of data using CRC-16 checksum.
# @name: verify_crc16
# @params:
# - data: The data to be checked for integrity. Should be a bytearray or a sequence of bytes.
# - received_crc: The received CRC-16 value to compare with the calculated CRC-16.
# @return: True if the calculated CRC-16 matches the received CRC-16, False otherwise.
def verify_crc16(data, received_crc):
    crc = 0xFFFF
    for byte in data:
        crc ^= byte << 8
        for _ in range(8):
            if crc & 0x8000:
                crc = (crc << 1) ^ 0x1021
            else:
                crc <<= 1
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

#
def readDataframe(filename):

    path = os.getcwd() + '/decoder/' + filename
    datas = []
    times = []
    try:
        with open(path, 'r') as file:
            lines = file.readlines()
            for line in lines:
                data, time = line.strip().split(',')
                datas.append(data)
                times.append(time)
    except:
        print(f"Error: the specified file was not found in {path}")

    return datas, times

#
def plotData(sensor_datas, title, labely):

    timestamps = [datetime.strptime(paire[1], '%d.%m.%Y %H:%M:%S') for paire in sensor_datas]
    datas = [paire[0] for paire in sensor_datas]

    # Création du graphique
    plt.plot(timestamps, datas, linestyle='-', color='blue')

    # Ajout d'étiquettes et de titres
    plt.xlabel("Date")
    plt.ylabel(labely)
    plt.title(title)

    # Formattage des horodatages sur l'axe x
    plt.xticks(rotation=45)

    # Affichage du graphique
    plt.tight_layout()
    plt.show()