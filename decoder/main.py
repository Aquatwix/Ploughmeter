import matplotlib.pyplot as plt
from datetime import datetime
import Functions
from Decoder import Decoder
Ploughmeter_CI = 0x08

# Load dataframes
dataframes, times = Functions.readDataframe("dataframe.txt")

temperatures = []
tiltsX = []
tiltsY = []
rolls = []
pitchs = []
yaws = []
p1s = []
t1s = []
p2s = []
t2s = []
p3s = []
t3s = []
p4s = []
t4s = []
PloughXs = []
PloughYs = []

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

        if(state_sensor["MAX31865"]):
            temp = a.getDataFromMAX31865()
            print(f"MAX31865:\tT: {temp}°C")

        if(state_sensor["SCL3300"]):
            tiltX, tiltY = a.getDataFromSCL3300()
            print(f"SCL3300:\tX: {tiltX}°\tY: {tiltY}°")

        if(state_sensor["ICM20948"]):
            roll, pitch, yaw = a.getDataFromICM20948()
            print(f"ICM20948:\tR: {roll}°\tP: {pitch}°\tY: {yaw}°")

        if(state_sensor["PAA-20LD1"]):
            p1, t1 = a.getDataFromPAA20LD_1()
            print(f"PAA-20LD (1):\tP: {p1} bar\tT: {t1}°C")

        if(state_sensor["PAA-20LD2"]):
            p2, t2 = a.getDataFromPAA20LD_2()
            print(f"PAA-20LD (2):\tP: {p2} bar\tT: {t2}°C")

        if(state_sensor["PAA-9LD"]):
            p3, t3 = a.getDataFromPAA9LD()
            print(f"PAA-9LD:\tP: {p3} bar\tT: {t3}°C")

        if(state_sensor["PD-10LX"]):
            p4, t4 = a.getDataFromPD10LX()
            print(f"PD-10LX:\tP: {p4} bar\tT: {t4}°C")

        if(state_sensor["NAU7802"]):
            PloughX, PloughY = a.getDataFromNAU7802()
            print(f"NAU7802:\tX: {PloughX}\tY: {PloughY}")

        if(a.CRCisValid()):
            print("CRC is correct.")

            if(state_sensor["MAX31865"]):
                temperatures.append((temp, time))   

            if(state_sensor["SCL3300"]):
                tiltsX.append((tiltX, time))   
                tiltsY.append((tiltY, time))   

            if(state_sensor["ICM20948"]):
                rolls.append((roll, time))
                pitchs.append((pitch, time))
                yaws.append((yaw, time))

            if(state_sensor["PAA-20LD1"]):
                p1s.append((p1, time))    
                t1s.append((t1, time))

            if(state_sensor["PAA-20LD2"]):
                p2s.append((p2, time))
                t2s.append((t2, time))

            if(state_sensor["PAA-9LD"]):
                p3s.append((p3, time))
                t3s.append((t3, time))

            if(state_sensor["PD-10LX"]):
                p4s.append((p4, time))
                t4s.append((t4, time))    

            if(state_sensor["NAU7802"]):
                PloughXs.append((PloughX, time))   
                PloughYs.append((PloughY, time))    
        else:
            print("The CRC calculated with the dataframe does not match with the one received.")
    else:
        print("Error: the IC found in the dataframe does not match the one you gave.")


# PLOTS ———————————————————————————————————————————————————————————

Functions.plotData(temperatures, "MAX31865", "Temperature (°C)")

# Functions.plotData(tiltsX, "SCL3300", "TiltX (°)")
# Functions.plotData(tiltsY, "SCL3300", "TiltY (°)")

# Functions.plotData(rolls, "ICM20948", "Roll (°)")
# Functions.plotData(pitchs, "ICM20948", "Pitch (°)")
# Functions.plotData(yaws, "ICM20948", "Yaw (°)")

# Functions.plotData(p1s, "PAA-20LD 1", "Pressure (bar)")
# Functions.plotData(t1s, "PAA-20LD 1", "Temperature (°C)")

# Functions.plotData(p2s, "PAA-20LD 2", "Pressure (bar)")
# Functions.plotData(t2s, "PAA-20LD 2", "Temperature (°C)")

# Functions.plotData(p3s, "PAA-9LD", "Pressure (bar)")
# Functions.plotData(t3s, "PAA-9LD", "Temperature (°C)")

# Functions.plotData(p4s, "PD-10LX", "Pressure (bar)")
# Functions.plotData(t4s, "PD-10LX", "Temperature (°C)")

# Functions.plotData(p1s, "NAU7802", "PloughX (bar)")
# Functions.plotData(t1s, "NAU7802", "PloughY (°C)")