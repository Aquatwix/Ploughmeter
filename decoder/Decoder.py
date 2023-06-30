import os
import Functions

class Decoder:

    # 
    def __init__(self):

        self.dataframe = 0
        self.Length_dataframe_int = 0
        self.CI_int = 0
        self.DC_code_int = 0
        self.Sensors_data_int = 0
        self.Length_data_int = 0
        self.crc = 0
        
        self.bytes_array = []        # Bytes must be save in bytes array to check the CRC
        self.states_sensors = {}

    # 
    def setDataframe(self, dataframe):

        DATA = {"Length":   dataframe[:2],  
                "CI":       dataframe[2:4],
                "DC_code":  dataframe[4:6],
                "Sensors":  dataframe[6:-4],
                "CRC":      dataframe[-4:]} 

        # Reading the dataframe
        self.dataframe = int(dataframe, 16)
        self.Length_dataframe_int = int(DATA["Length"], 16)  # Length of the dataframe
        self.CI_int = int(DATA["CI"], 16)                    # CI received
        self.DC_code_int = int(DATA["DC_code"], 16)          # DC Code received
        self.Sensors_data_int = int(DATA["Sensors"], 16)     # Data Received
        self.Length_data_int = len(DATA["Sensors"])          # Length of the data (without length, ci, dc code and crc)
        self.crc = int(DATA["CRC"], 16)

    #
    def checkingCI(self, CI_Ploughmeter):
        return (self.CI_int == CI_Ploughmeter)
    
    #
    def addByteInArray(self, byte):
        self.bytes_array.append(byte)

    #
    def loadHeader(self):

        #- Header must start with : Length of the packet + CI (then data...)
        self.addByteInArray(int((self.Length_dataframe_int/2)+1)) # -_____________________________WARRRRRNINNNNG
        self.addByteInArray(self.CI_int)

    #
    def loadLength(self):

        self.addByteInArray(self.Length_dataframe_int)
        return self.Length_dataframe_int

    #
    def loadCI(self):

        self.addByteInArray(self.CI_int)
        return self.CI_int

    #
    def loadDetectedCode(self):

        self.addByteInArray(self.DC_code_int)

        # Update the state of sensors according to DC Code
        self.states_sensors["MAX31865"] = self.DC_code_int >> 7
        self.states_sensors["SCL3300"] = (self.DC_code_int >> 6) & 0x1
        self.states_sensors["ICM20948"] = (self.DC_code_int >> 5) & 0x1
        self.states_sensors["PAA-20LD1"] = (self.DC_code_int >> 4) & 0x1
        self.states_sensors["PAA-20LD2"] = (self.DC_code_int >> 3) & 0x1
        self.states_sensors["PAA-9LD"] = (self.DC_code_int >> 2) & 0x1
        self.states_sensors["PD-10LX"] = (self.DC_code_int >> 1) & 0x1
        self.states_sensors["NAU7802"] = self.DC_code_int & 0x1 

        return self.DC_code_int, self.states_sensors
    
    #
    def CRCisValid(self):

        self.addByteInArray(0x0)
        self.addByteInArray(0x0)
        return Functions.verify_crc16(self.bytes_array, self.crc)

    #
    def updateData(self, amount_bytes):

        try:
            self.Sensors_data_int = int(hex(self.Sensors_data_int)[(amount_bytes*2)+2:], 16)         # Remove the data
            self.Length_data_int = len(hex(self.Sensors_data_int)) - 2                               # Update the length
        except:
            # print("End of the data.")
            pass
    
    #
    def getDataFromMAX31865(self):

        amount_byte_rtd = 2  # Represents 4 nibbles
        RTD_int = self.Sensors_data_int >> ((self.Length_data_int - (amount_byte_rtd * 2)) * 4)  # Shifting to extract the RTD value in binary
        RTD_int_1 = RTD_int >> 8                          # Extracting first byte of RTD value
        RTD_int_2 = RTD_int & 0x00FF                      # Extracting second byte of RTD value
        self.addByteInArray(RTD_int_1)                     # Appending first byte to bytes_array
        self.addByteInArray(RTD_int_2)                     # Appending second byte to bytes_array
        self.updateData(amount_byte_rtd)

        return round(Functions.RTD_to_temp(RTD_int), 2)

    #
    def getDataFromSCL3300(self):

        # TiltX 
        amount_byte_tiltx = 2  # Represents 4 nibbles
        TiltX_int = self.Sensors_data_int >> ((self.Length_data_int - (amount_byte_tiltx * 2)) * 4)  # Shifting to extract the TiltX value in binary
        TiltX_int_1 = TiltX_int >> 8
        TiltX_int_2 = TiltX_int & 0x00FF
        self.addByteInArray(TiltX_int_1)
        self.addByteInArray(TiltX_int_2)
        TiltX = (TiltX_int-18000)/100
        self.updateData(amount_byte_tiltx)

        # TiltY 
        amount_byte_tilty = 2
        TiltY_int = self.Sensors_data_int >> ((self.Length_data_int - (amount_byte_tilty * 2)) * 4)  # Shifting to extract the TiltY value in binary
        TiltY_int_1 = TiltY_int >> 8
        TiltY_int_2 = TiltY_int & 0x00FF
        self.addByteInArray(TiltY_int_1)
        self.addByteInArray(TiltY_int_2)
        TiltY = (TiltY_int-18000)/100
        self.updateData(amount_byte_tilty)

        return TiltX, TiltY
    
    #
    def getDataFromICM20948(self):

        # Roll 
        amount_byte_roll = 2  # Represents 4 nibbles
        Roll_int = self.Sensors_data_int >> ((self.Length_data_int - (amount_byte_roll * 2)) * 4)  # Shifting to extract the Roll value in binary
        Roll_int_1 = Roll_int >> 8
        Roll_int_2 = Roll_int & 0x00FF
        self.addByteInArray(Roll_int_1)
        self.addByteInArray(Roll_int_2)
        roll = (Roll_int-18000)/100
        self.updateData(amount_byte_roll)

        # Pitch 
        amount_byte_pitch = 2
        Pitch_int = self.Sensors_data_int >> ((self.Length_data_int - (amount_byte_pitch * 2)) * 4)  # Shifting to extract the Pitch value in binary
        Pitch_int_1 = Pitch_int >> 8
        Pitch_int_2 = Pitch_int & 0x00FF
        self.addByteInArray(Pitch_int_1)
        self.addByteInArray(Pitch_int_2)
        pitch = (Pitch_int-18000)/100
        self.updateData(amount_byte_pitch)

        # Yaw 
        amount_byte_yaw = 2
        Yaw_int = self.Sensors_data_int >> ((self.Length_data_int - (amount_byte_yaw * 2)) * 4)  # Shifting to extract the Yaw value in binary
        Yaw_int_1 = Yaw_int >> 8
        Yaw_int_2 = Yaw_int & 0x00FF
        self.addByteInArray(Yaw_int_1)
        self.addByteInArray(Yaw_int_2)
        yaw = (Yaw_int-18000)/100
        self.updateData(amount_byte_yaw)

        return roll, pitch, yaw

    #
    def getDataFromPAA20LD_1(self):
        
        #- Pressure
        amount_byte_pressure_paa20_1 = 2  # Represents 4 nibbles
        PAA20_P1_int = self.Sensors_data_int >> ((self.Length_data_int - (amount_byte_pressure_paa20_1 * 2)) * 4)  # Shifting to extract the pressure value in binary
        PAA20_P1_int_1 = PAA20_P1_int >> 8
        PAA20_P1_int_2 = PAA20_P1_int & 0x00FF
        self.addByteInArray(PAA20_P1_int_1)
        self.addByteInArray(PAA20_P1_int_2)
        PAA20_P1 = round((PAA20_P1_int-16384)*(40/32768), 4)
        self.updateData(amount_byte_pressure_paa20_1)

        #- Temperature
        amount_byte_temp_paa20_1 = 2  # Represents 4 nibbles
        PAA20_T1_int = self.Sensors_data_int >> ((self.Length_data_int - (amount_byte_temp_paa20_1 * 2)) * 4)  # Shifting to extract the temp value in binary
        PAA20_T1_int_1 = PAA20_T1_int >> 8
        PAA20_T1_int_2 = PAA20_T1_int & 0x00FF
        self.addByteInArray(PAA20_T1_int_1)
        self.addByteInArray(PAA20_T1_int_2)
        PAA20_T1 = round((((PAA20_T1_int >> 4) - 24) * 0.05) - 50, 3)
        self.updateData(amount_byte_temp_paa20_1)

        return PAA20_P1, PAA20_T1

    #
    def getDataFromPAA20LD_2(self):
        
        #- Pressure
        amount_byte_pressure_paa20_2 = 2  # Represents 4 nibbles
        PAA20_P2_int = self.Sensors_data_int >> ((self.Length_data_int - (amount_byte_pressure_paa20_2 * 2)) * 4)  # Shifting to extract the pressure value in binary
        PAA20_P2_int_1 = PAA20_P2_int >> 8
        PAA20_P2_int_2 = PAA20_P2_int & 0x00FF
        self.addByteInArray(PAA20_P2_int_1)
        self.addByteInArray(PAA20_P2_int_2)
        PAA20_P2 = round((PAA20_P2_int-16384)*(40/32768), 4)
        self.updateData(amount_byte_pressure_paa20_2)

        #- Temperature
        amount_byte_temp_paa20_2 = 2  # Represents 4 nibbles
        PAA20_T2_int = self.Sensors_data_int >> ((self.Length_data_int - (amount_byte_temp_paa20_2 * 2)) * 4)  # Shifting to extract the temperature value in binary
        PAA20_T2_int_1 = PAA20_T2_int >> 8
        PAA20_T2_int_2 = PAA20_T2_int & 0x00FF
        self.addByteInArray(PAA20_T2_int_1)
        self.addByteInArray(PAA20_T2_int_2)
        PAA20_T2 = round((((PAA20_T2_int >> 4) - 24) * 0.05) - 50, 3)
        self.updateData(amount_byte_temp_paa20_2)

        return PAA20_P2, PAA20_T2

    #
    def getDataFromPAA9LD(self):
        
        #- Pressure
        amount_byte_pressure_paa9 = 2  # Represents 4 nibbles
        PAA9_P_int = self.Sensors_data_int >> ((self.Length_data_int - (amount_byte_pressure_paa9 * 2)) * 4)  # Shifting to extract the temperature value in binary
        PAA9_P_int_1 = PAA9_P_int >> 8
        PAA9_P_int_2 = PAA9_P_int & 0x00FF
        self.addByteInArray(PAA9_P_int_1)
        self.addByteInArray(PAA9_P_int_2)
        PAA9_P = round((PAA9_P_int-16384)*(40/32768), 4)
        self.updateData(amount_byte_pressure_paa9)

        #- Temperature
        amount_byte_temp_paa9 = 2  # Represents 4 nibbles
        PAA9_T_int = self.Sensors_data_int >> ((self.Length_data_int - (amount_byte_temp_paa9 * 2)) * 4)  # Shifting to extract the temperature value in binary
        PAA9_T_int_1 = PAA9_T_int >> 8
        PAA9_T_int_2 = PAA9_T_int & 0x00FF
        self.addByteInArray(PAA9_T_int_1)
        self.addByteInArray(PAA9_T_int_2)
        PAA9_T = round((((PAA9_T_int >> 4) - 24) * 0.05) - 50, 3)
        self.updateData(amount_byte_temp_paa9)

        return PAA9_P, PAA9_T

    #
    def getDataFromPD10LX(self):
        
        #- Pressure
        amount_byte_pressure_pd10 = 2
        PD10_P_int = self.Sensors_data_int >> ((self.Length_data_int - (amount_byte_pressure_pd10 * 2)) * 4)  # Shifting to extract the temperature value in binary
        PD10_P_int_1 = PD10_P_int >> 8
        PD10_P_int_2 = PD10_P_int & 0x00FF
        self.addByteInArray(PD10_P_int_1)
        self.addByteInArray(PD10_P_int_2)
        PD10_P = round((PD10_P_int - 10000) / 10000, 4)
        self.updateData(amount_byte_pressure_pd10)

        #- Temperature
        amount_byte_temp_pd10 = 2
        PD10_T_int = self.Sensors_data_int >> ((self.Length_data_int - (amount_byte_temp_pd10 * 2)) * 4)  # Shifting to extract the temperature value in binary
        PD10_T_int_1 = PD10_T_int >> 8
        PD10_T_int_2 = PD10_T_int & 0x00FF
        self.addByteInArray(PD10_T_int_1)
        self.addByteInArray(PD10_T_int_2)
        PD10_T = round((PD10_T_int - 30000)/100, 3)
        self.updateData(amount_byte_temp_pd10)

        return PD10_P, PD10_T

    #
    def getDataFromNAU7802(self):
        
        # PloughX 
        amount_byte_ploughx = 3
        PloughX_int = self.Sensors_data_int >> ((self.Length_data_int - (amount_byte_ploughx * 2)) * 4)  # Shifting to extract the temperature value in binary
        PloughX_int_1 = PloughX_int >> 16
        PloughX_int_2 = (PloughX_int >> 8) & 0x00FF
        PloughX_int_3 = PloughX_int & 0x0000FF
        self.addByteInArray(PloughX_int_1)
        self.addByteInArray(PloughX_int_2)
        self.addByteInArray(PloughX_int_3)
        self.updateData(amount_byte_ploughx)

        # PloughY 
        amount_byte_ploughy = 3
        PloughY_int = self.Sensors_data_int >> ((self.Length_data_int - (amount_byte_ploughy * 2)) * 4)  # Shifting to extract the temperature value in binary
        PloughY_int_1 = PloughY_int >> 16
        PloughY_int_2 = (PloughY_int >> 8) & 0x00FF
        PloughY_int_3 = PloughY_int & 0x0000FF
        self.addByteInArray(PloughY_int_1)
        self.addByteInArray(PloughY_int_2)
        self.addByteInArray(PloughY_int_3)
        self.updateData(amount_byte_ploughy)

        return PloughX_int, PloughY_int

    #
    def information(self):

        print(f"Dataframe: {hex(self.dataframe)}")
        print(f"Length_dataframe_int: {self.Length_dataframe_int}")
        print(f"Sensors_data_int: {hex(self.Sensors_data_int)}")
        print(f"Length_data_int: {int(self.Length_data_int)}")
        print(f"CI_int: {hex(self.CI_int)}")
        print(f"DC_code_int: {hex(self.DC_code_int)}")