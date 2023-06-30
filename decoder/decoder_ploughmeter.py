import math
import os

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


# ——————————————————————————————————————————————————————————————————————————————————————————————————————————————
# ———————————————————————————————————————————————————— MAIN ————————————————————————————————————————————————————
# ——————————————————————————————————————————————————————————————————————————————————————————————————————————————

bytes_array = []        # Bytes must be save in bytes array to check the CRC
CI_Ploughmeter = 0x08   # CI of the Ploughmeter
DATAFRAME = "3608F1209323CC46CE45EB45CC1A9343346098123456789ABC7A9D"

SIZE_DATAFRAME = len(DATAFRAME)     # add -2 if DATA starts with 0x
DATA = {"Length":   DATAFRAME[:2],  
        "CI":       DATAFRAME[2:4],
        "DC_code":  DATAFRAME[4:6],
        "Sensors":  DATAFRAME[6:-4],
        "CRC":      DATAFRAME[-4:]} 

# Reading the dataframe
Length_dataframe_int = int(DATA["Length"], 16)  # Length of the dataframe
CI_int = int(DATA["CI"], 16)                    # CI received
DC_code_int = int(DATA["DC_code"], 16)          # DC Code received
Sensors_data_int = int(DATA["Sensors"], 16)     # Data Received
Length_data_int = len(DATA["Sensors"])          # Length of the data (without length, ci, dc code and crc)
print("Data : ", hex(Sensors_data_int), " Length Data : ", Length_data_int)

# Verification : CI
if(CI_int == CI_Ploughmeter):

    #- Header must start with : Length of the packet + CI (then data...)
    bytes_array.append(Length_dataframe_int)
    bytes_array.append(CI_int)
    #- Length
    bytes_array.append(Length_dataframe_int)
    print(f"Length:\t\t{hex(Length_dataframe_int)}")
    #- CI
    bytes_array.append(CI_int)
    print(f"CI:\t\t{hex(CI_int)}")

    # DC Code —————————————————————————————————————————————————
    bytes_array.append(DC_code_int)
    print(f"DCode:\t\t{hex(DC_code_int)}")

    # Update the state of sensors accroding to DC Code
    states_sensors = {}
    states_sensors["MAX31865"] = DC_code_int >> 7
    states_sensors["SCL3300"] = (DC_code_int >> 6) & 0x1
    states_sensors["ICM20948"] = (DC_code_int >> 5) & 0x1
    states_sensors["PAA-20LD1"] = (DC_code_int >> 4) & 0x1
    states_sensors["PAA-20LD2"] = (DC_code_int >> 3) & 0x1
    states_sensors["PAA-9LD"] = (DC_code_int >> 2) & 0x1
    states_sensors["PD-10LX"] = (DC_code_int >> 1) & 0x1
    states_sensors["NAU7802"] = DC_code_int & 0x1 

    # RTD ——————————————————————————————————————————————————————
    if states_sensors["MAX31865"]:

        amount_byte_rtd = 2  # Represents 4 nibbles
        RTD_int = Sensors_data_int >> ((Length_data_int - (amount_byte_rtd * 2)) * 4)  # Shifting to extract the RTD value in binary
        RTD_int_1 = RTD_int >> 8                          # Extracting first byte of RTD value
        RTD_int_2 = RTD_int & 0x00FF                      # Extracting second byte of RTD value
        bytes_array.append(RTD_int_1)                     # Appending first byte to bytes_array
        bytes_array.append(RTD_int_2)                     # Appending second byte to bytes_array
        temp = round(RTD_to_temp(RTD_int), 2)             # Converting RTD value to temperature
        print(f"RTD:\t\t{hex(RTD_int)}\t\t{temp} °C") 

        # Udpate the data and the length 
        try:
            Sensors_data_int = int(hex(Sensors_data_int)[(amount_byte_rtd*2)+2:], 16)      # Remove RTD data in the DATA
            Length_data_int = len(hex(Sensors_data_int)) - 2                               # Update the length
        except:
            print("End of the data.")

    # Tilt —————————————————————————————————————————————————————
    if(states_sensors["SCL3300"]):

        # TiltX 
        amount_byte_tiltx = 2  # Represents 4 nibbles
        TiltX_int = Sensors_data_int >> ((Length_data_int - (amount_byte_tiltx * 2)) * 4)  # Shifting to extract the TiltX value in binary
        
        TiltX_int_1 = TiltX_int >> 8
        TiltX_int_2 = TiltX_int & 0x00FF
        bytes_array.append(TiltX_int_1)
        bytes_array.append(TiltX_int_2)
        TiltX = (TiltX_int-18000)/100
        print(f"TiltX:\t\t{hex(TiltX_int)}\t\t{TiltX} deg")

        # Udpate the data and the length 
        try:
            Sensors_data_int = int(hex(Sensors_data_int)[(amount_byte_tiltx*2)+2:], 16)      # Remove TiltX data in the DATA
            Length_data_int = len(hex(Sensors_data_int)) - 2  
        except:
            print("End of the data.")

        # TiltY 
        amount_byte_tilty = 2
        TiltY_int = Sensors_data_int >> ((Length_data_int - (amount_byte_tilty * 2)) * 4)  # Shifting to extract the TiltY value in binary
        TiltY_int_1 = TiltY_int >> 8
        TiltY_int_2 = TiltY_int & 0x00FF
        bytes_array.append(TiltY_int_1)
        bytes_array.append(TiltY_int_2)
        TiltY = (TiltY_int-18000)/100
        print(f"TiltY:\t\t{hex(TiltY_int)}\t\t{TiltY} deg")

        # Udpate the data and the length 
        try:
            Sensors_data_int = int(hex(Sensors_data_int)[(amount_byte_tilty*2)+2:], 16)      # Remove TiltY data in the DATA
            Length_data_int = len(hex(Sensors_data_int)) - 2 
        except:
            print("End of the data.")

    # IMU ——————————————————————————————————————————————————————
    if(states_sensors["ICM20948"]):

        # Roll 
        amount_byte_roll = 2  # Represents 4 nibbles
        Roll_int = Sensors_data_int >> ((Length_data_int - (amount_byte_roll * 2)) * 4)  # Shifting to extract the Roll value in binary
        Roll_int_1 = Roll_int >> 8
        Roll_int_2 = Roll_int & 0x00FF
        bytes_array.append(Roll_int_1)
        bytes_array.append(Roll_int_2)
        Roll = (Roll_int-18000)/100
        print(f"Roll:\t\t{hex(Roll_int)}\t\t{Roll} deg")

        # Udpate the data and the length 
        try:
            Sensors_data_int = int(hex(Sensors_data_int)[(amount_byte_roll*2)+2:], 16)      # Remove Roll data in the DATA
            Length_data_int = len(hex(Sensors_data_int)) - 2 
        except:
            print("End of the data.")

        # Pitch 
        amount_byte_pitch = 2
        Pitch_int = Sensors_data_int >> ((Length_data_int - (amount_byte_pitch * 2)) * 4)  # Shifting to extract the Pitch value in binary
        Pitch_int_1 = Pitch_int >> 8
        Pitch_int_2 = Pitch_int & 0x00FF
        bytes_array.append(Pitch_int_1)
        bytes_array.append(Pitch_int_2)
        Pitch = (Pitch_int-18000)/100
        print(f"Pitch:\t\t{hex(Pitch_int)}\t\t{Pitch} deg")

        # Udpate the data and the length 
        try:
            Sensors_data_int = int(hex(Sensors_data_int)[(amount_byte_pitch*2)+2:], 16)      # Remove Pitch data in the DATA
            Length_data_int = len(hex(Sensors_data_int)) - 2 
        except:
            print("End of the data.")

        # Yaw 
        amount_byte_yaw = 2
        Yaw_int = Sensors_data_int >> ((Length_data_int - (amount_byte_yaw * 2)) * 4)  # Shifting to extract the Yaw value in binary
        Yaw_int_1 = Yaw_int >> 8
        Yaw_int_2 = Yaw_int & 0x00FF
        bytes_array.append(Yaw_int_1)
        bytes_array.append(Yaw_int_2)
        Yaw = (Yaw_int-18000)/100
        print(f"Yaw:\t\t{hex(Yaw_int)}\t\t{Yaw} deg")

        # Udpate the data and the length 
        try:
            Sensors_data_int = int(hex(Sensors_data_int)[(amount_byte_yaw*2)+2:], 16)      # Remove Yaw data in the DATA
            Length_data_int = len(hex(Sensors_data_int)) - 2 
        except:
            print("End of the data.")

    # PAA-20D (1) ——————————————————————————————————————————————
    if(states_sensors["PAA-20LD1"]):

        #- Pressure
        amount_byte_pressure_paa20_1 = 2  # Represents 4 nibbles
        PAA20_P1_int = Sensors_data_int >> ((Length_data_int - (amount_byte_pressure_paa20_1 * 2)) * 4)  # Shifting to extract the pressure value in binary
        PAA20_P1_int_1 = PAA20_P1_int >> 8
        PAA20_P1_int_2 = PAA20_P1_int & 0x00FF
        bytes_array.append(PAA20_P1_int_1)
        bytes_array.append(PAA20_P1_int_2)
        PAA20_P1 = round((PAA20_P1_int-16384)*(40/32768), 4)
        print(f"P1:\t\t{hex(PAA20_P1_int)}\t\t{PAA20_P1} bar")

        # Udpate the data and the length 
        try:
            Sensors_data_int = int(hex(Sensors_data_int)[(amount_byte_pressure_paa20_1*2)+2:], 16)      # Remove Roll data in the DATA
            Length_data_int = len(hex(Sensors_data_int)) - 2 
        except:
            print("End of the data.")

        #- Temperature
        amount_byte_temp_paa20_1 = 2  # Represents 4 nibbles
        PAA20_T1_int = Sensors_data_int >> ((Length_data_int - (amount_byte_temp_paa20_1 * 2)) * 4)  # Shifting to extract the temp value in binary
        PAA20_T1_int_1 = PAA20_T1_int >> 8
        PAA20_T1_int_2 = PAA20_T1_int & 0x00FF
        bytes_array.append(PAA20_T1_int_1)
        bytes_array.append(PAA20_T1_int_2)
        PAA20_T1 = round((((PAA20_T1_int >> 4) - 24) * 0.05) - 50, 3)
        print(f"T1:\t\t{hex(PAA20_T1_int)}\t\t{PAA20_T1} °C")

        # Udpate the data and the length 
        try:
            Sensors_data_int = int(hex(Sensors_data_int)[(amount_byte_temp_paa20_1*2)+2:], 16)      # Remove Roll data in the DATA
            Length_data_int = len(hex(Sensors_data_int)) - 2 
        except:
            print("End of the data.")

    # PAA-20D (2) ——————————————————————————————————————————————
    if(states_sensors["PAA-20LD2"]):

        #- Pressure
        amount_byte_pressure_paa20_2 = 2  # Represents 4 nibbles
        PAA20_P2_int = Sensors_data_int >> ((Length_data_int - (amount_byte_pressure_paa20_2 * 2)) * 4)  # Shifting to extract the pressure value in binary
        PAA20_P2_int_1 = PAA20_P2_int >> 8
        PAA20_P2_int_2 = PAA20_P2_int & 0x00FF
        bytes_array.append(PAA20_P2_int_1)
        bytes_array.append(PAA20_P2_int_2)
        PAA20_P2 = round((PAA20_P2_int-16384)*(40/32768), 4)
        print(f"P2:\t\t{hex(PAA20_P2_int)}\t\t{PAA20_P2} bar")

        # Udpate the data and the length 
        try:
            Sensors_data_int = int(hex(Sensors_data_int)[(amount_byte_pressure_paa20_2*2)+2:], 16)      # Remove Pressure data in the DATA
            Length_data_int = len(hex(Sensors_data_int)) - 2 
        except:
            print("End of the data.")

        #- Temperature
        amount_byte_temp_paa20_2 = 2  # Represents 4 nibbles
        PAA20_T2_int = Sensors_data_int >> ((Length_data_int - (amount_byte_temp_paa20_2 * 2)) * 4)  # Shifting to extract the temperature value in binary
        PAA20_T2_int_1 = PAA20_T2_int >> 8
        PAA20_T2_int_2 = PAA20_T2_int & 0x00FF
        bytes_array.append(PAA20_T2_int_1)
        bytes_array.append(PAA20_T2_int_2)
        PAA20_T2 = round((((PAA20_T2_int >> 4) - 24) * 0.05) - 50, 3)
        print(f"T2:\t\t{hex(PAA20_T2_int)}\t\t{PAA20_T2} °C")

        # Udpate the data and the length 
        try:
            Sensors_data_int = int(hex(Sensors_data_int)[(amount_byte_temp_paa20_2*2)+2:], 16)      # Remove Temperautre data in the DATA
            Length_data_int = len(hex(Sensors_data_int)) - 2 
        except:
            print("End of the data.")

    # PAA-9D ———————————————————————————————————————————————————
    if(states_sensors["PAA-9LD"]):

        #- Pressure
        amount_byte_pressure_paa9 = 2  # Represents 4 nibbles
        PAA9_P_int = Sensors_data_int >> ((Length_data_int - (amount_byte_pressure_paa9 * 2)) * 4)  # Shifting to extract the temperature value in binary
        PAA9_P_int_1 = PAA9_P_int >> 8
        PAA9_P_int_2 = PAA9_P_int & 0x00FF
        bytes_array.append(PAA9_P_int_1)
        bytes_array.append(PAA9_P_int_2)
        PAA9_P = round((PAA9_P_int-16384)*(40/32768), 4)
        print(f"P3:\t\t{hex(PAA9_P_int)}\t\t{PAA9_P} bar")

        # Udpate the data and the length 
        try:
            Sensors_data_int = int(hex(Sensors_data_int)[(amount_byte_pressure_paa9*2)+2:], 16)      # Remove Pressure data in the DATA
            Length_data_int = len(hex(Sensors_data_int)) - 2 
        except:
            print("End of the data.")

        #- Temperature
        amount_byte_temp_paa9 = 2  # Represents 4 nibbles
        PAA9_T_int = Sensors_data_int >> ((Length_data_int - (amount_byte_temp_paa9 * 2)) * 4)  # Shifting to extract the temperature value in binary
        PAA9_T_int_1 = PAA9_T_int >> 8
        PAA9_T_int_2 = PAA9_T_int & 0x00FF
        bytes_array.append(PAA9_T_int_1)
        bytes_array.append(PAA9_T_int_2)
        PAA9_T = round((((PAA9_T_int >> 4) - 24) * 0.05) - 50, 3)
        print(f"T3:\t\t{hex(PAA9_T_int)}\t\t{PAA9_T} °C")

        # Udpate the data and the length 
        try:
            Sensors_data_int = int(hex(Sensors_data_int)[(amount_byte_temp_paa9*2)+2:], 16)      # Remove Temperature data in the DATA
            Length_data_int = len(hex(Sensors_data_int)) - 2 
        except:
            print("End of the data.")

    # PD-10LX ——————————————————————————————————————————————————
    if(states_sensors["PD-10LX"]):

        #- Pressure
        amount_byte_pressure_pd10 = 2
        PD10_P_int = Sensors_data_int >> ((Length_data_int - (amount_byte_pressure_pd10 * 2)) * 4)  # Shifting to extract the temperature value in binary
        PD10_P_int_1 = PD10_P_int >> 8
        PD10_P_int_2 = PD10_P_int & 0x00FF
        bytes_array.append(PD10_P_int_1)
        bytes_array.append(PD10_P_int_2)
        PD10_P = round((PD10_P_int - 10000) / 10000, 4)
        print(f"P4:\t\t{hex(PD10_P_int)}\t\t{PD10_P} mbar")

        # Udpate the data and the length 
        try:
            Sensors_data_int = int(hex(Sensors_data_int)[(amount_byte_pressure_pd10*2)+2:], 16)      # Remove Temperautre data in the DATA
            Length_data_int = len(hex(Sensors_data_int)) - 2 
        except:
            print("End of the data.")

        #- Temperature
        amount_byte_temp_pd10 = 2
        PD10_T_int = Sensors_data_int >> ((Length_data_int - (amount_byte_temp_pd10 * 2)) * 4)  # Shifting to extract the temperature value in binary
        PD10_T_int_1 = PD10_T_int >> 8
        PD10_T_int_2 = PD10_T_int & 0x00FF
        bytes_array.append(PD10_T_int_1)
        bytes_array.append(PD10_T_int_2)
        PD10_T = round((PD10_T_int - 30000)/100, 3)
        print(f"T4:\t\t{hex(PD10_T_int)}\t\t{PD10_T} °C")

        # Udpate the data and the length 
        try:
            Sensors_data_int = int(hex(Sensors_data_int)[(amount_byte_temp_pd10*2)+2:], 16)      # Remove Temperautre data in the DATA
            Length_data_int = len(hex(Sensors_data_int)) - 2 
        except:
            print("End of the data.")
        
    # Strain gages —————————————————————————————————————————————
    if(states_sensors["NAU7802"]):

            # PloughX 
            amount_byte_ploughx = 3
            PloughX_int = Sensors_data_int >> ((Length_data_int - (amount_byte_ploughx * 2)) * 4)  # Shifting to extract the temperature value in binary
            PloughX_int_1 = PloughX_int >> 16
            PloughX_int_2 = (PloughX_int >> 8) & 0x00FF
            PloughX_int_3 = PloughX_int & 0x0000FF
            bytes_array.append(PloughX_int_1)
            bytes_array.append(PloughX_int_2)
            bytes_array.append(PloughX_int_3)
            print(f"GageX:\t\t{hex(PloughX_int)}\t{PloughX_int}")

            # Udpate the data and the length 
            try:
                Sensors_data_int = int(hex(Sensors_data_int)[(amount_byte_ploughx*2)+2:], 16)      # Remove RTD data in the DATA
                Length_data_int = len(hex(Sensors_data_int)) - 2                               # Update the length
            except:
                print("End of the data.")

            # PloughY 
            amount_byte_ploughy = 3
            PloughY_int = Sensors_data_int >> ((Length_data_int - (amount_byte_ploughy * 2)) * 4)  # Shifting to extract the temperature value in binary
            PloughY_int_1 = PloughY_int >> 16
            PloughY_int_2 = (PloughY_int >> 8) & 0x00FF
            PloughY_int_3 = PloughY_int & 0x0000FF
            bytes_array.append(PloughY_int_1)
            bytes_array.append(PloughY_int_2)
            bytes_array.append(PloughY_int_3)
            print(f"GageY:\t\t{hex(PloughY_int)}\t{PloughY_int}")

            # Udpate the data and the length 
            try:
                Sensors_data_int = int(hex(Sensors_data_int)[(amount_byte_ploughy*2)+2:], 16)      # Remove RTD data in the DATA
                Length_data_int = len(hex(Sensors_data_int)) - 2                               # Update the length
            except:
                print("End of the data.")

# CRC ——————————————————————————————————————————————————————
CRC_int = int(DATA["CRC"], 16)
crc_is_valid = verify_crc16(bytes_array, CRC_int)
print(f"CRC:\t\t{hex(CRC_int)}\t\t", "Correct" if crc_is_valid else "Incorrect")