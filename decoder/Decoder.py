import Functions

class Decoder:

    # 
    def __init__(self):

        self.dataframe = 0
        self.Length_dataframe_int = 0
        self.CI_int = 0
        self.DC_code_int = 0
        self.Sensors_data_int = ""
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
        self.Sensors_data_int = DATA["Sensors"]              # Data Received
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
        self.addByteInArray(self.Length_dataframe_int)
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
            self.Sensors_data_int = self.Sensors_data_int[amount_bytes*2:]
            self.Length_data_int = len(self.Sensors_data_int)                               # Update the length
        except:
            # print("End of the data.")
            pass
    
    #
    def getDataFromMAX31865(self):
        
        amount_byte_rtd = 2  # Represents 4 nibbles
        RTD_int = format(int(self.Sensors_data_int, 16) >> ((self.Length_data_int - (amount_byte_rtd * 2)) * 4), '04X')  # Shifting to extract the RTD value in binary
        RTD_int_1 = format(int(RTD_int, 16) >> 8, '02X')                         # Extracting first byte of RTD value
        RTD_int_2 = format(int(RTD_int, 16) & 0x00FF, '02X')                      # Extracting second byte of RTD value
        self.addByteInArray(int(RTD_int_1, 16))                     # Appending first byte to bytes_array
        self.addByteInArray(int(RTD_int_2, 16))                     # Appending second byte to bytes_array
        self.updateData(amount_byte_rtd)

        return round(Functions.RTD_to_temp(int(RTD_int, 16)), 2)

    #
    def getDataFromSCL3300(self):

        # TiltX 
        amount_byte_tiltx = 2  # Represents 4 nibbles
        TiltX_int = format(int(self.Sensors_data_int, 16) >> ((self.Length_data_int - (amount_byte_tiltx * 2)) * 4), '04X')  # Shifting to extract the TiltX value in binary
        TiltX_int_1 = format(int(TiltX_int, 16) >> 8, '02X')
        TiltX_int_2 = format(int(TiltX_int, 16) & 0x00FF, '02X')
        self.addByteInArray(int(TiltX_int_1, 16))
        self.addByteInArray(int(TiltX_int_2, 16))
        TiltX = (int(TiltX_int, 16)-18000)/100
        self.updateData(amount_byte_tiltx)

        # TiltY 
        amount_byte_tilty = 2
        TiltY_int = format(int(self.Sensors_data_int, 16) >> ((self.Length_data_int - (amount_byte_tilty * 2)) * 4), '04X')  # Shifting to extract the TiltY value in binary
        TiltY_int_1 = format(int(TiltY_int, 16) >> 8, '02X')
        TiltY_int_2 = format(int(TiltY_int, 16) & 0x00FF, '02X')
        self.addByteInArray(int(TiltY_int_1, 16))
        self.addByteInArray(int(TiltY_int_2, 16))
        TiltY = (int(TiltY_int,16)-18000)/100
        self.updateData(amount_byte_tilty)

        return TiltX, TiltY
    
    #
    def getDataFromICM20948(self):

        # Roll 
        amount_byte_roll = 2  # Represents 4 nibbles
        Roll_int = format(int(self.Sensors_data_int, 16) >> ((self.Length_data_int - (amount_byte_roll * 2)) * 4), '04X')  # Shifting to extract the Roll value in binary
        Roll_int_1 = format(int(Roll_int, 16) >> 8, '02X')
        Roll_int_2 = format(int(Roll_int, 16) & 0x00FF, '02X')
        self.addByteInArray(int(Roll_int_1, 16))
        self.addByteInArray(int(Roll_int_2, 16))
        roll = (int(Roll_int, 16)-18000)/100
        self.updateData(amount_byte_roll)

        # Pitch 
        amount_byte_pitch = 2
        Pitch_int = format(int(self.Sensors_data_int, 16) >> ((self.Length_data_int - (amount_byte_pitch * 2)) * 4), '04X')  # Shifting to extract the Pitch value in binary
        Pitch_int_1 = format(int(Pitch_int, 16) >> 8, '02X')
        Pitch_int_2 = format(int(Pitch_int, 16) & 0x00FF, '02X')
        self.addByteInArray(int(Pitch_int_1, 16))
        self.addByteInArray(int(Pitch_int_2, 16))
        pitch = (int(Pitch_int, 16)-18000)/100
        self.updateData(amount_byte_pitch)

        # Yaw 
        amount_byte_yaw = 2
        Yaw_int = format(int(self.Sensors_data_int, 16) >> ((self.Length_data_int - (amount_byte_yaw * 2)) * 4), '04X')  # Shifting to extract the Yaw value in binary
        Yaw_int_1 = format(int(Yaw_int, 16) >> 8, '02X')
        Yaw_int_2 = format(int(Yaw_int, 16) & 0x00FF, '02X')
        self.addByteInArray(int(Yaw_int_1, 16))
        self.addByteInArray(int(Yaw_int_2, 16))
        yaw = (int(Yaw_int, 16)-18000)/100
        self.updateData(amount_byte_yaw)

        return roll, pitch, yaw

    #
    def getDataFromPAA20LD_1(self):

        #- Pressure
        amount_byte_pressure_paa20_1 = 2  # Represents 4 nibbles
        PAA20_P1_int = format(int(self.Sensors_data_int, 16) >> ((self.Length_data_int - (amount_byte_pressure_paa20_1 * 2)) * 4), '04X')  # Shifting to extract the pressure value in binary
        PAA20_P1_int_1 = format(int(PAA20_P1_int, 16) >> 8, '02X')
        PAA20_P1_int_2 = format(int(PAA20_P1_int, 16) & 0x00FF, '02X')
        self.addByteInArray(int(PAA20_P1_int_1, 16))
        self.addByteInArray(int(PAA20_P1_int_2, 16))
        PAA20_P1 = round((int(PAA20_P1_int, 16)-16384)*(40/32768), 4)
        self.updateData(amount_byte_pressure_paa20_1)

        #- Temperature
        amount_byte_temp_paa20_1 = 2  # Represents 4 nibbles
        PAA20_T1_int = format(int(self.Sensors_data_int, 16) >> ((self.Length_data_int - (amount_byte_temp_paa20_1 * 2)) * 4), '04X')  # Shifting to extract the temp value in binary
        PAA20_T1_int_1 = format(int(PAA20_T1_int, 16) >> 8, '02X')
        PAA20_T1_int_2 = format(int(PAA20_T1_int, 16) & 0x00FF, '02X')
        self.addByteInArray(int(PAA20_T1_int_1, 16))
        self.addByteInArray(int(PAA20_T1_int_2, 16))
        PAA20_T1 = round((((int(PAA20_T1_int, 16) >> 4) - 24) * 0.05) - 50, 3)
        self.updateData(amount_byte_temp_paa20_1)

        return PAA20_P1, PAA20_T1

    #
    def getDataFromPAA20LD_2(self):
        
        #- Pressure
        amount_byte_pressure_paa20_2 = 2  # Represents 4 nibbles
        PAA20_P2_int = format(int(self.Sensors_data_int, 16) >> ((self.Length_data_int - (amount_byte_pressure_paa20_2 * 2)) * 4), '04X') # Shifting to extract the pressure value in binary
        PAA20_P2_int_1 = format(int(PAA20_P2_int, 16) >> 8, '02X')
        PAA20_P2_int_2 = format(int(PAA20_P2_int, 16) & 0x00FF, '02X')
        self.addByteInArray(int(PAA20_P2_int_1, 16))
        self.addByteInArray(int(PAA20_P2_int_2, 16))
        PAA20_P2 = round((int(PAA20_P2_int, 16)-16384)*(40/32768), 4)
        self.updateData(amount_byte_pressure_paa20_2)

        #- Temperature
        amount_byte_temp_paa20_2 = 2  # Represents 4 nibbles
        PAA20_T2_int = format(int(self.Sensors_data_int, 16) >> ((self.Length_data_int - (amount_byte_temp_paa20_2 * 2)) * 4), '04X')  # Shifting to extract the temperature value in binary
        PAA20_T2_int_1 = format(int(PAA20_T2_int, 16) >> 8, '02X')
        PAA20_T2_int_2 = format(int(PAA20_T2_int, 16) & 0x00FF, '02X')
        self.addByteInArray(int(PAA20_T2_int_1, 16))
        self.addByteInArray(int(PAA20_T2_int_2, 16))
        PAA20_T2 = round((((int(PAA20_T2_int, 16) >> 4) - 24) * 0.05) - 50, 3)
        self.updateData(amount_byte_temp_paa20_2)

        return PAA20_P2, PAA20_T2

    #
    def getDataFromPAA9LD(self):
        
        #- Pressure
        amount_byte_pressure_paa9 = 2  # Represents 4 nibbles
        PAA9_P_int = format(int(self.Sensors_data_int, 16) >> ((self.Length_data_int - (amount_byte_pressure_paa9 * 2)) * 4), '04X')  # Shifting to extract the temperature value in binary
        PAA9_P_int_1 = format(int(PAA9_P_int, 16) >> 8, '02X')
        PAA9_P_int_2 = format(int(PAA9_P_int, 16) & 0x00FF, '02X')
        self.addByteInArray(int(PAA9_P_int_1, 16))
        self.addByteInArray(int(PAA9_P_int_2, 16))
        PAA9_P = round((int(PAA9_P_int, 16)-16384)*(40/32768), 4)
        self.updateData(amount_byte_pressure_paa9)

        #- Temperature
        amount_byte_temp_paa9 = 2  # Represents 4 nibbles
        PAA9_T_int = format(int(self.Sensors_data_int, 16) >> ((self.Length_data_int - (amount_byte_temp_paa9 * 2)) * 4), '04X')  # Shifting to extract the temperature value in binary
        PAA9_T_int_1 = format(int(PAA9_T_int, 16) >> 8, '02X')
        PAA9_T_int_2 = format(int(PAA9_T_int, 16) & 0x00FF, '02X')
        self.addByteInArray(int(PAA9_T_int_1, 16))
        self.addByteInArray(int(PAA9_T_int_2, 16))
        PAA9_T = round((((int(PAA9_T_int, 16) >> 4) - 24) * 0.05) - 50, 3)
        self.updateData(amount_byte_temp_paa9)

        return PAA9_P, PAA9_T

    #
    def getDataFromPD10LX(self):
        
        #- Pressure
        amount_byte_pressure_pd10 = 2
        PD10_P_int = format(int(self.Sensors_data_int, 16) >> ((self.Length_data_int - (amount_byte_pressure_pd10 * 2)) * 4), '04X')  # Shifting to extract the temperature value in binary
        PD10_P_int_1 = format(int(PD10_P_int, 16) >> 8, '02X')
        PD10_P_int_2 = format(int(PD10_P_int, 16) & 0x00FF, '02X')
        self.addByteInArray(int(PD10_P_int_1, 16))
        self.addByteInArray(int(PD10_P_int_2, 16))
        PD10_P = round((int(PD10_P_int, 16) - 10000) / 10000, 4)
        self.updateData(amount_byte_pressure_pd10)

        #- Temperature
        amount_byte_temp_pd10 = 2
        PD10_T_int = format(int(self.Sensors_data_int, 16) >> ((self.Length_data_int - (amount_byte_temp_pd10 * 2)) * 4), '04X')  # Shifting to extract the temperature value in binary
        PD10_T_int_1 = format(int(PD10_T_int, 16) >> 8, '02X')
        PD10_T_int_2 = format(int(PD10_T_int, 16) & 0x00FF, '02X')
        self.addByteInArray(int(PD10_T_int_1, 16))
        self.addByteInArray(int(PD10_T_int_2, 16))
        PD10_T = round((int(PD10_T_int, 16) - 30000)/100, 3)
        self.updateData(amount_byte_temp_pd10)

        return PD10_P, PD10_T

    #
    def getDataFromNAU7802(self):
        
        # PloughX 
        amount_byte_ploughx = 3
        PloughX_int = format(int(self.Sensors_data_int, 16) >> ((self.Length_data_int - (amount_byte_ploughx * 2)) * 4), '06X')  # Shifting to extract the temperature value in binary
        PloughX_int_1 = format(int(PloughX_int, 16) >> 16, '02X')
        PloughX_int_2 = format((int(PloughX_int, 16) >> 8) & 0x00FF, '02X')
        PloughX_int_3 = format(int(PloughX_int, 16) & 0x0000FF, '02X')
        self.addByteInArray(int(PloughX_int_1, 16))
        self.addByteInArray(int(PloughX_int_2, 16))
        self.addByteInArray(int(PloughX_int_3, 16))
        self.updateData(amount_byte_ploughx)

        # PloughY 
        amount_byte_ploughy = 3
        PloughY_int = format(int(self.Sensors_data_int, 16) >> ((self.Length_data_int - (amount_byte_ploughy * 2)) * 4), '06X')  # Shifting to extract the temperature value in binary
        PloughY_int_1 = format(int(PloughY_int, 16) >> 16, '02X')
        PloughY_int_2 = format((int(PloughY_int, 16) >> 8) & 0x00FF, '02X')
        PloughY_int_3 = format(int(PloughY_int, 16) & 0x0000FF, '02X')
        self.addByteInArray(int(PloughY_int_1, 16))
        self.addByteInArray(int(PloughY_int_2, 16))
        self.addByteInArray(int(PloughY_int_3, 16))
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