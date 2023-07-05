import Functions

class Decoder:

    """ ———————————————————————————————————————————————————————————————————
    Initializes a new instance of the Decoder class.
    """
    def __init__(self):

        self.dataframe = 0              # Holds the dataframe
        self.Length_dataframe_int = 0   # Length of the dataframe
        self.CI_int = 0                 # CI value
        self.DC_code_int = 0            # DC code
        self.Sensors_data_int = ""      # Sensor data
        self.Length_data_int = 0        # Length of the data
        self.crc = 0                    # CRC value

        self.bytes_array = []           # Bytes must be saved in a bytes array to check the CRC
        self.states_sensors = {}        # Dictionary to hold sensor states


    """ ———————————————————————————————————————————————————————————————————
    Sets the values of the Decoder instance based on the provided dataframe.
    @param dataframe: The input dataframe.
    """
    def setDataframe(self, dataframe):

        # Parsing the dataframe into individual components
        DATA = {
            "Length":   dataframe[:2],    # Length of the dataframe
            "CI":       dataframe[2:4],    # CI value
            "DC_code":  dataframe[4:6],    # DC code
            "Sensors":  dataframe[6:-4],   # Sensor data
            "CRC":      dataframe[-4:]     # CRC value
        } 

        # Setting the values of the Decoder instance
        self.dataframe = int(dataframe, 16)                    # The entire dataframe as an integer
        self.Length_dataframe_int = int(DATA["Length"], 16)    # Length of the dataframe
        self.CI_int = int(DATA["CI"], 16)                      # CI received
        self.DC_code_int = int(DATA["DC_code"], 16)            # DC Code received
        self.Sensors_data_int = DATA["Sensors"]                # Data Received
        self.Length_data_int = len(DATA["Sensors"])            # Length of the data (without length, ci, dc code, and crc)
        self.crc = int(DATA["CRC"], 16)                        # CRC value


    """ ———————————————————————————————————————————————————————————————————
    Checks if the CI value matches the provided CI_Ploughmeter.
    @param CI_Ploughmeter: The CI value to compare.
    @return: True if the CI values match, False otherwise.
    """
    def checkingCI(self, CI_Ploughmeter):
        return (self.CI_int == CI_Ploughmeter)


    """ ———————————————————————————————————————————————————————————————————
    Adds a byte to the bytes_array list.
    @param byte: The byte to add.
    """
    def addByteInArray(self, byte):
        self.bytes_array.append(byte)


    """ ———————————————————————————————————————————————————————————————————
    Loads the header bytes into the bytes_array.
    - Header must start with: Length of the packet + CI (then data...)
    """
    def loadHeader(self):

        self.addByteInArray(self.Length_dataframe_int)
        self.addByteInArray(self.CI_int)


    """ ———————————————————————————————————————————————————————————————————
    Loads the length byte into the bytes_array.
    @return: The Length_dataframe_int value.
    """
    def loadLength(self):

        self.addByteInArray(self.Length_dataframe_int)
        return self.Length_dataframe_int


    """ ———————————————————————————————————————————————————————————————————
    Loads the CI byte into the bytes_array.
    @return: The CI_int value.
    """
    def loadCI(self):

        self.addByteInArray(self.CI_int)
        return self.CI_int


    """ ———————————————————————————————————————————————————————————————————
        Loads the DC_code byte into the bytes_array and updates the states of sensors based on the DC Code.
        @return: The DC_code_int value and the updated states_sensors dictionary.
    """
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


    """ ———————————————————————————————————————————————————————————————————
    Adds two zero bytes to the bytes_array and verifies the CRC value.
    @return: True if the CRC is valid, False otherwise.
    """
    def CRCisValid(self):
        self.addByteInArray(0x0)
        self.addByteInArray(0x0)
        return Functions.verify_crc16(self.bytes_array, self.crc)


    """ ———————————————————————————————————————————————————————————————————
    Updates the Sensors_data_int and Length_data_int based on the provided amount of bytes.
    @param amount_bytes: The number of bytes to update.
    """
    def updateData(self, amount_bytes):

        try:
            self.Sensors_data_int = self.Sensors_data_int[amount_bytes*2:]
            self.Length_data_int = len(self.Sensors_data_int)  # Update the length
        except:
            # print("End of the data.")
            pass


    """ ———————————————————————————————————————————————————————————————————
    Extracts the data from the MAX31865 sensor in Sensors_data_int and updates the bytes_array and data.
    @return: The rounded temperature value extracted from the MAX31865 sensor.
    """
    def getDataFromMAX31865(self):

        amount_byte_rtd = 2  # Represents 4 nibbles
        RTD_int = format(int(self.Sensors_data_int, 16) >> ((self.Length_data_int - (amount_byte_rtd * 2)) * 4), '04X')  # Shifting to extract the RTD value in binary
        RTD_int_1 = format(int(RTD_int, 16) >> 8, '02X')                         # Extracting first byte of RTD value
        RTD_int_2 = format(int(RTD_int, 16) & 0x00FF, '02X')                      # Extracting second byte of RTD value
        self.addByteInArray(int(RTD_int_1, 16))                     # Appending first byte to bytes_array
        self.addByteInArray(int(RTD_int_2, 16))                     # Appending second byte to bytes_array
        self.updateData(amount_byte_rtd)

        return round(Functions.RTD_to_temp(int(RTD_int, 16)), 2)


    """ ———————————————————————————————————————————————————————————————————
    Extracts the data from the SCL3300 sensor in Sensors_data_int and updates the bytes_array and data.
    @return: The TiltX and TiltY values extracted from the SCL3300 sensor.
    """
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


    """ ———————————————————————————————————————————————————————————————————
    Extracts the data from the ICM20948 sensor in Sensors_data_int and updates the bytes_array and data.
    @return: The Roll, Pitch, and Yaw values extracted from the ICM20948 sensor.
    """
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


    """ ———————————————————————————————————————————————————————————————————
    Extracts the data from the PAA20LD_1 sensor in Sensors_data_int and updates the bytes_array and data.
    @return: The Pressure and Temperature values extracted from the PAA20LD_1 sensor.
    """
    def getDataFromPAA20LD_1(self):

        # Pressure
        amount_byte_pressure_paa20_1 = 2  # Represents 4 nibbles
        PAA20_P1_int = format(int(self.Sensors_data_int, 16) >> ((self.Length_data_int - (amount_byte_pressure_paa20_1 * 2)) * 4), '04X')  # Shifting to extract the pressure value in binary
        PAA20_P1_int_1 = format(int(PAA20_P1_int, 16) >> 8, '02X')
        PAA20_P1_int_2 = format(int(PAA20_P1_int, 16) & 0x00FF, '02X')
        self.addByteInArray(int(PAA20_P1_int_1, 16))
        self.addByteInArray(int(PAA20_P1_int_2, 16))
        PAA20_P1 = round((int(PAA20_P1_int, 16)-16384)*(40/32768), 4)
        self.updateData(amount_byte_pressure_paa20_1)

        # Temperature
        amount_byte_temp_paa20_1 = 2  # Represents 4 nibbles
        PAA20_T1_int = format(int(self.Sensors_data_int, 16) >> ((self.Length_data_int - (amount_byte_temp_paa20_1 * 2)) * 4), '04X')  # Shifting to extract the temp value in binary
        PAA20_T1_int_1 = format(int(PAA20_T1_int, 16) >> 8, '02X')
        PAA20_T1_int_2 = format(int(PAA20_T1_int, 16) & 0x00FF, '02X')
        self.addByteInArray(int(PAA20_T1_int_1, 16))
        self.addByteInArray(int(PAA20_T1_int_2, 16))
        PAA20_T1 = round((((int(PAA20_T1_int, 16) >> 4) - 24) * 0.05) - 50, 3)
        self.updateData(amount_byte_temp_paa20_1)

        return PAA20_P1, PAA20_T1


    """ ———————————————————————————————————————————————————————————————————
    Extracts the data from the PAA20LD_2 sensor in Sensors_data_int and updates the bytes_array and data.
    @return: The Pressure and Temperature values extracted from the PAA20LD_2 sensor.
    """
    def getDataFromPAA20LD_2(self):

        # Pressure
        amount_byte_pressure_paa20_2 = 2  # Represents 4 nibbles
        PAA20_P2_int = format(int(self.Sensors_data_int, 16) >> ((self.Length_data_int - (amount_byte_pressure_paa20_2 * 2)) * 4), '04X')  # Shifting to extract the pressure value in binary
        PAA20_P2_int_1 = format(int(PAA20_P2_int, 16) >> 8, '02X')
        PAA20_P2_int_2 = format(int(PAA20_P2_int, 16) & 0x00FF, '02X')
        self.addByteInArray(int(PAA20_P2_int_1, 16))
        self.addByteInArray(int(PAA20_P2_int_2, 16))
        PAA20_P2 = round((int(PAA20_P2_int, 16)-16384)*(40/32768), 4)
        self.updateData(amount_byte_pressure_paa20_2)

        # Temperature
        amount_byte_temp_paa20_2 = 2  # Represents 4 nibbles
        PAA20_T2_int = format(int(self.Sensors_data_int, 16) >> ((self.Length_data_int - (amount_byte_temp_paa20_2 * 2)) * 4), '04X')  # Shifting to extract the temperature value in binary
        PAA20_T2_int_1 = format(int(PAA20_T2_int, 16) >> 8, '02X')
        PAA20_T2_int_2 = format(int(PAA20_T2_int, 16) & 0x00FF, '02X')
        self.addByteInArray(int(PAA20_T2_int_1, 16))
        self.addByteInArray(int(PAA20_T2_int_2, 16))
        PAA20_T2 = round((((int(PAA20_T2_int, 16) >> 4) - 24) * 0.05) - 50, 3)
        self.updateData(amount_byte_temp_paa20_2)

        return PAA20_P2, PAA20_T2


    """ ———————————————————————————————————————————————————————————————————
    Extracts the data from the PAA9LD sensor in Sensors_data_int and updates the bytes_array and data.
    @return: The Pressure and Temperature values extracted from the PAA9LD sensor.
    """
    def getDataFromPAA9LD(self):

        # Pressure
        amount_byte_pressure_paa9 = 2  # Represents 4 nibbles
        PAA9_P_int = format(int(self.Sensors_data_int, 16) >> ((self.Length_data_int - (amount_byte_pressure_paa9 * 2)) * 4), '04X')  # Shifting to extract the pressure value in binary
        PAA9_P_int_1 = format(int(PAA9_P_int, 16) >> 8, '02X')
        PAA9_P_int_2 = format(int(PAA9_P_int, 16) & 0x00FF, '02X')
        self.addByteInArray(int(PAA9_P_int_1, 16))
        self.addByteInArray(int(PAA9_P_int_2, 16))
        PAA9_P = round((int(PAA9_P_int, 16)-16384)*(40/32768), 4)
        self.updateData(amount_byte_pressure_paa9)

        # Temperature
        amount_byte_temp_paa9 = 2  # Represents 4 nibbles
        PAA9_T_int = format(int(self.Sensors_data_int, 16) >> ((self.Length_data_int - (amount_byte_temp_paa9 * 2)) * 4), '04X')  # Shifting to extract the temperature value in binary
        PAA9_T_int_1 = format(int(PAA9_T_int, 16) >> 8, '02X')
        PAA9_T_int_2 = format(int(PAA9_T_int, 16) & 0x00FF, '02X')
        self.addByteInArray(int(PAA9_T_int_1, 16))
        self.addByteInArray(int(PAA9_T_int_2, 16))
        PAA9_T = round((((int(PAA9_T_int, 16) >> 4) - 24) * 0.05) - 50, 3)
        self.updateData(amount_byte_temp_paa9)

        return PAA9_P, PAA9_T


    """ ———————————————————————————————————————————————————————————————————
    Extracts the data from the PD10LX sensor in Sensors_data_int and updates the bytes_array and data.
    @return: The Pressure and Temperature values extracted from the PD10LX sensor.
    """
    def getDataFromPD10LX(self):

        # Pressure
        amount_byte_pressure_pd10 = 2
        PD10_P_int = format(int(self.Sensors_data_int, 16) >> ((self.Length_data_int - (amount_byte_pressure_pd10 * 2)) * 4), '04X')  # Shifting to extract the pressure value in binary
        PD10_P_int_1 = format(int(PD10_P_int, 16) >> 8, '02X')
        PD10_P_int_2 = format(int(PD10_P_int, 16) & 0x00FF, '02X')
        self.addByteInArray(int(PD10_P_int_1, 16))
        self.addByteInArray(int(PD10_P_int_2, 16))
        PD10_P = round((int(PD10_P_int, 16) - 10000) / 10000, 4)
        self.updateData(amount_byte_pressure_pd10)

        # Temperature
        amount_byte_temp_pd10 = 2
        PD10_T_int = format(int(self.Sensors_data_int, 16) >> ((self.Length_data_int - (amount_byte_temp_pd10 * 2)) * 4), '04X')  # Shifting to extract the temperature value in binary
        PD10_T_int_1 = format(int(PD10_T_int, 16) >> 8, '02X')
        PD10_T_int_2 = format(int(PD10_T_int, 16) & 0x00FF, '02X')
        self.addByteInArray(int(PD10_T_int_1, 16))
        self.addByteInArray(int(PD10_T_int_2, 16))
        PD10_T = round((int(PD10_T_int, 16) - 30000) / 100, 3)
        self.updateData(amount_byte_temp_pd10)

        return PD10_P, PD10_T


    """ ———————————————————————————————————————————————————————————————————
    Extracts the data from the NAU7802 sensor in Sensors_data_int and updates the bytes_array and data.
    @return: The PloughX and PloughY values extracted from the NAU7802 sensor.
    """
    def getDataFromNAU7802(self):

        # PloughX
        amount_byte_ploughx = 3
        PloughX_int = format(int(self.Sensors_data_int, 16) >> ((self.Length_data_int - (amount_byte_ploughx * 2)) * 4), '06X')  # Shifting to extract the PloughX value in binary
        PloughX_int_1 = format(int(PloughX_int, 16) >> 16, '02X')
        PloughX_int_2 = format((int(PloughX_int, 16) >> 8) & 0x00FF, '02X')
        PloughX_int_3 = format(int(PloughX_int, 16) & 0x0000FF, '02X')
        self.addByteInArray(int(PloughX_int_1, 16))
        self.addByteInArray(int(PloughX_int_2, 16))
        self.addByteInArray(int(PloughX_int_3, 16))
        self.updateData(amount_byte_ploughx)

        # PloughY
        amount_byte_ploughy = 3
        PloughY_int = format(int(self.Sensors_data_int, 16) >> ((self.Length_data_int - (amount_byte_ploughy * 2)) * 4), '06X')  # Shifting to extract the PloughY value in binary
        PloughY_int_1 = format(int(PloughY_int, 16) >> 16, '02X')
        PloughY_int_2 = format((int(PloughY_int, 16) >> 8) & 0x00FF, '02X')
        PloughY_int_3 = format(int(PloughY_int, 16) & 0x0000FF, '02X')
        self.addByteInArray(int(PloughY_int_1, 16))
        self.addByteInArray(int(PloughY_int_2, 16))
        self.addByteInArray(int(PloughY_int_3, 16))
        self.updateData(amount_byte_ploughy)

        offset = 5642200
        return int(PloughX_int, 16) - offset, int(PloughY_int, 16) - offset


    """ ———————————————————————————————————————————————————————————————————
    Prints information about the object's attributes.
    """
    def information(self):

        print(f"Dataframe: {hex(self.dataframe)}")
        print(f"Length_dataframe_int: {self.Length_dataframe_int}")
        print(f"Sensors_data_int: {hex(self.Sensors_data_int)}")
        print(f"Length_data_int: {int(self.Length_data_int)}")
        print(f"CI_int: {hex(self.CI_int)}")
        print(f"DC_code_int: {hex(self.DC_code_int)}")
