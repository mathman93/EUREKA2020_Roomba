## Imports ##

import time
import serial
import csv
import os
import socket

## Globals, and Variables, and Inputs, Oh My ##

global Xbee # Specifies connection to Xbee
Xbee = serial.Serial('/dev/ttyUSB0', 115200) # Baud rate should be 115200
heading = int(input("Please enter your heading: "))
FileName = input("Enter File Name (Do Not Add .csv): ")
RecordTime = .01 #Every half a second, record data
threshold = 360
frequency = 180 # Degrees/second
CycleTime = threshold/frequency # Amount of time it takes nodephase to get form 0 to 360 degrees
CouplingStrength = .75

## Data Collection Stuff ##
FullName = FileName + '.csv'
path = os.path.join('..', 'Data_Files', FullName)
file = open(path, 'w', newline='')
csvWriter = csv.writer(file)
csvWriter.writerow(['Time Stamp', 'Phase Value', 'Heading', 'Ping?'])

## Main Code ##
time1 = time.time() - (time.time() % CycleTime) # Time reference
Timer = time.time() - time1
nodephase = heading + (Timer * frequencey)
if nodephase >= threshold:
    time1 += CycleTime

ToWrite = []
start = time.time()
CurrentTime = start
WriteTimer = CurrentTime + RecordTime

while True:

    try:
        CurrentTime = time.time()

        ## Increasing the phase value ##
        Timer = time.time() - time1
        nodephase = heading + (Timer * frequency)

        ## Reaching the Threshold and Sending Pulses ##
        if nodephase >= threshold:
            message = "T"
            Xbee.write(message.encode()) #Send the letter over the Xbee
            ToWrite.append([time.time(), 360, heading, 1])
            ToWrite.append([time.time(), 0, heading, 0])
            time1 += CycleTime

            start = CurrentTime
            WriteTimer = start + RecordTime

            print("Pulse Sent")
            print("The phase value is: %f" % nodephase)

        ## Receiving Pulses and Adjusting Phase Value ##
        if Xbee.inWaiting() > 0: # If there is something in the receive buffer of the Xbee
            message = Xbee.read(Xbee.inWaiting()).decode() # Read all data in
            ToWrite.append([time.time(), nodephase, heading, 0])
            print(message) # To see what the message is
            if 0 < nodephase <= 180: # Adjusting nodephase based on heading
                heading -= nodephase * CouplingStrength
            if 180 < nodephase <= threshold: # Adjusting nodephase based on heading
                heading += (threshold - nodephase) * CouplingStrength
            if heading >= threshold:
                heading -= threshold
                time1 -= CycleTime
                print("The heading is: %f" % heading)
            if heading <= 0:
                heading += threshold
                time1 += CycleTime
                print("The heading is: %f" % heading)
            ToWrite.append([time.time(), nodephase, heading, 0])
            print("The phase value is: %f" % nodephase)

        ## Recording Data ##
        if CurrentTime >= WriteTimer:
            ToWrite.append([time.time(), nodephase, heading, 0])
            WriteTimer  += RecordTime

    ## Keyboard Interupt ##
    except KeyboardInterrupt:
        print('')
        break
    
    ## If the input is not a number ##
    except type(nodephase) == str:
        print("Please enter a number.")

## Ending Code ##
csvWriter.writerows(ToWrite)
file.close()
Xbee.close()


