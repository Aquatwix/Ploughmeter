import matplotlib.pyplot as plt
from datetime import datetime
import Functions
from Decoder import Decoder
Ploughmeter_CI = 0x08

# Load dataframes
dataframes, times = Functions.readDataframe("dataframe.txt")
MAX31865_DATAS, SCL3300_DATAS, ICM20948_DATAS, PAA20LD1_DATAS, PAA20LD2_DATAS, PAA9LD_DATAS, PD10LX_DATAS, NAU7802_DATAS = [], [], [], [], [], [], [], []

# Browse the data frame file, retrieving frame, rssi and timestamp line by line.
for dataframe, time in zip(dataframes, times):

    print("——————————————————————————————————————————————————————")
    a = Decoder()
    a.setDataframe(dataframe)
    # a.information()

    if(a.checkingCI(Ploughmeter_CI)):

        a.loadHeader()
        length = a.loadLength()
        ci = a.loadCI()
        dc_code, state_sensor = a.loadDetectedCode()
        print(f"Frame : \t0x{a.Sensors_data_int}")

        if(state_sensor["MAX31865"]):
            temp = a.getDataFromMAX31865()
        if(state_sensor["SCL3300"]):
            tiltX, tiltY = a.getDataFromSCL3300()
        if(state_sensor["ICM20948"]):
            roll, pitch, yaw = a.getDataFromICM20948()       
        if(state_sensor["PAA-20LD1"]):
            p1, t1 = a.getDataFromPAA20LD_1()   
        if(state_sensor["PAA-20LD2"]):
            p2, t2 = a.getDataFromPAA20LD_2()
        if(state_sensor["PAA-9LD"]):
            p3, t3 = a.getDataFromPAA9LD()
        if(state_sensor["PD-10LX"]):
            p4, t4 = a.getDataFromPD10LX()
        if(state_sensor["NAU7802"]):
            PloughX, PloughY = a.getDataFromNAU7802()

        # Consider only data that is reliable (with the correct CRC)
        if(a.CRCisValid()):

            if(state_sensor["MAX31865"]):
                MAX31865_DATAS.append((temp, time))
                print(f"MAX31865:\tT: {temp}°C")
            if(state_sensor["SCL3300"]):
                SCL3300_DATAS.append((tiltX, tiltY, time))   
                print(f"SCL3300:\tX: {tiltX}°\tY: {tiltY}°")  
            if(state_sensor["ICM20948"]):
                ICM20948_DATAS.append((roll, pitch, yaw, time))
                print(f"ICM20948:\tR: {roll}°\tP: {pitch}°\tY: {yaw}°")
            if(state_sensor["PAA-20LD1"]):
                PAA20LD1_DATAS.append((p1, t1, time))    
                print(f"PAA-20LD (1):\tP: {p1} bar\tT: {t1}°C")
            if(state_sensor["PAA-20LD2"]):
                PAA20LD2_DATAS.append((p2, t2, time))  
                print(f"PAA-20LD (2):\tP: {p2} bar\tT: {t2}°C")
            if(state_sensor["PAA-9LD"]):
                PAA9LD_DATAS.append((p3, t3, time))
                print(f"PAA-9LD:\tP: {p3} bar\tT: {t3}°C")
            if(state_sensor["PD-10LX"]):
                PD10LX_DATAS.append((p4, t4, time))
                print(f"PD-10LX:\tP: {p4} bar\tT: {t4}°C")   
            if(state_sensor["NAU7802"]):
                NAU7802_DATAS.append((PloughX, PloughY, time))   
                print(f"NAU7802:\tX: {PloughX}\tY: {PloughY}")    
        else:
            print("The CRC calculated with the dataframe does not match with the one received.")
    else:
        print("Error: the IC found in the dataframe does not match the one you gave.")


# PLOTS ———————————————————————————————————————————————————————————

# Create a plot with a 2x4 grid
fig, axs = plt.subplots(2, 4, figsize=(16, 8))
fig.suptitle("Displaying sensors data")

# Call the functions to plot the data on the graphs
Functions.plotMAX31865Data(MAX31865_DATAS)
Functions.plotSCL3300Data(SCL3300_DATAS)
Functions.plotICM20948Data(ICM20948_DATAS)
Functions.plotPAA20D1Data(PAA20LD1_DATAS)
Functions.plotPAA20D2Data(PAA20LD2_DATAS)
Functions.plotPAA9LDData(PAA9LD_DATAS)
Functions.plotPD10LXData(PD10LX_DATAS)
Functions.plotNAU7802Data(NAU7802_DATAS)

# Adjust the spacing between subplots
plt.tight_layout()

# Display the plot
plt.show()
