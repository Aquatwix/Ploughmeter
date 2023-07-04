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
    datas, rssis, times = [], [], []
    try:
        with open(path, 'r') as file:
            lines = file.readlines()
            for line in lines:
                data, rssi, time = line.strip().split('	')
                datas.append(data)
                rssis.append(rssi)
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



def plotMAX31865Data(temperatures):
    timestamps = [datetime.strptime(paire[1], '%d.%m.%Y %H:%M:%S') for paire in temperatures]
    datas = [paire[0] for paire in temperatures]

    # Création du graphique pour MAX31865
    plt.subplot(2, 4, 1)
    plt.plot(timestamps, datas, linestyle='-', color='blue')
    plt.scatter(timestamps, datas, color='blue', marker='o', s=10)
    plt.xlabel("Date")
    plt.ylabel("Temperature (°C)")
    plt.title("MAX31865")
    plt.xticks(rotation=45)


def plotSCL3300Data(tilts):
    timestamps = [datetime.strptime(paire[2], '%d.%m.%Y %H:%M:%S') for paire in tilts]
    tiltX = [paire[0] for paire in tilts]
    tiltY = [paire[1] for paire in tilts]

    # Création du graphique pour SCL3300
    plt.subplot(2, 4, 2)
    plt.plot(timestamps, tiltX, linestyle='-', color='blue', label='TiltX')
    plt.plot(timestamps, tiltY, linestyle='-', color='red', label='TiltY')
    plt.scatter(timestamps, tiltX, color='blue', marker='o', s=10)
    plt.scatter(timestamps, tiltY, color='red', marker='o', s=10)
    plt.xlabel("Date")
    plt.ylabel("Angle (°)")
    plt.title("SCL3300")
    plt.xticks(rotation=45)
    plt.legend()

def plotICM20948Data(angles):
    timestamps = [datetime.strptime(paire[3], '%d.%m.%Y %H:%M:%S') for paire in angles]
    roll = [paire[0] for paire in angles]
    pitch = [paire[1] for paire in angles]
    yaw = [paire[2] for paire in angles]

    # Création du graphique pour ICM20948
    plt.subplot(2, 4, 3)
    plt.plot(timestamps, roll, linestyle='-', color='blue', label='Roll')
    plt.plot(timestamps, pitch, linestyle='-', color='red', label='Pitch')
    plt.plot(timestamps, yaw, linestyle='-', color='green', label='Yaw')
    plt.scatter(timestamps, roll, color='blue', marker='o', s=10)
    plt.scatter(timestamps, pitch, color='red', marker='o', s=10)
    plt.scatter(timestamps, yaw, color='green', marker='o', s=10)
    plt.xlabel("Date")
    plt.ylabel("Angle (°)")
    plt.title("ICM20948")
    plt.xticks(rotation=45)
    plt.legend()

def plotPAA20D1Data(datas):
    timestamps = [datetime.strptime(paire[2], '%d.%m.%Y %H:%M:%S') for paire in datas]
    p = [paire[0] for paire in datas]
    t = [paire[1] for paire in datas]

    # Création du graphique pour PAA20D1
    plt.subplot(2, 4, 4)
    plt.plot(timestamps, p, linestyle='-', color='blue', label='Pressure')
    plt.plot(timestamps, t, linestyle='-', color='red', label='Temperature')
    plt.scatter(timestamps, p, color='blue', marker='o', s=10)
    plt.scatter(timestamps, t, color='red', marker='o', s=10)
    plt.xlabel("Date")
    plt.ylabel("Bar and °C")
    plt.title("PAA-20D 1")
    plt.xticks(rotation=45)
    plt.legend()

def plotPAA20D2Data(datas):
    timestamps = [datetime.strptime(paire[2], '%d.%m.%Y %H:%M:%S') for paire in datas]
    p = [paire[0] for paire in datas]
    t = [paire[1] for paire in datas]

    # Création du graphique pour PAA20D2
    plt.subplot(2, 4, 5)
    plt.plot(timestamps, p, linestyle='-', color='blue', label='Pressure')
    plt.plot(timestamps, t, linestyle='-', color='red', label='Temperature')
    plt.scatter(timestamps, p, color='blue', marker='o', s=10)
    plt.scatter(timestamps, t, color='red', marker='o', s=10)
    plt.xlabel("Date")
    plt.ylabel("Bar and °C")
    plt.title("PAA-20D 2")
    plt.xticks(rotation=45)
    plt.legend()

def plotPAA9LDData(datas):
    timestamps = [datetime.strptime(paire[2], '%d.%m.%Y %H:%M:%S') for paire in datas]
    p = [paire[0] for paire in datas]
    t = [paire[1] for paire in datas]

    # Création du graphique pour PAA9LD
    plt.subplot(2, 4, 6)
    plt.plot(timestamps, p, linestyle='-', color='blue', label='Pressure')
    plt.plot(timestamps, t, linestyle='-', color='red', label='Temperature')
    plt.scatter(timestamps, p, color='blue', marker='o', s=10)
    plt.scatter(timestamps, t, color='red', marker='o', s=10)
    plt.xlabel("Date")
    plt.ylabel("Bar and °C")
    plt.title("PAA-9LD")
    plt.xticks(rotation=45)
    plt.legend()

def plotPD10LXData(datas):
    timestamps = [datetime.strptime(paire[2], '%d.%m.%Y %H:%M:%S') for paire in datas]
    p = [paire[0] for paire in datas]
    t = [paire[1] for paire in datas]

    # Création du graphique pour PD10LX
    plt.subplot(2, 4, 7)
    plt.plot(timestamps, p, linestyle='-', color='blue', label='Pressure')
    plt.plot(timestamps, t, linestyle='-', color='red', label='Temperature')
    plt.scatter(timestamps, p, color='blue', marker='o', s=10)
    plt.scatter(timestamps, t, color='red', marker='o', s=10)
    plt.xlabel("Date")
    plt.ylabel("Bar and °C")
    plt.title("PD-10LX")
    plt.xticks(rotation=45)
    plt.legend()

def plotNAU7802Data(datas):
    timestamps = [datetime.strptime(paire[2], '%d.%m.%Y %H:%M:%S') for paire in datas]
    ploughX = [paire[0] for paire in datas]
    ploughY = [paire[1] for paire in datas]

    # Création du graphique pour PD10LX
    plt.subplot(2, 4, 8)
    plt.plot(timestamps, ploughX, linestyle='-', color='blue', label='PloughX')
    plt.plot(timestamps, ploughY, linestyle='-', color='red', label='PloughY')
    plt.scatter(timestamps, ploughX, color='blue', marker='o', s=10)
    plt.scatter(timestamps, ploughY, color='red', marker='o', s=10)
    plt.xlabel("Date")
    plt.ylabel("Value")
    plt.title("NAU7802")
    plt.xticks(rotation=45)
    plt.legend()
