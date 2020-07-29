## Imports ##

import time
import serial

## Globals and Variables ##

global Xbee # Specifies connection to Xbee
Xbee = serial.Serial('/dev/ttyUSB0', 115200) # Baud rate should be 115200
heading = int(input("Please enter your heading: "))
RecordTime = .5 # Every half a second, record data
threshold = 360
frequency = 12 # Degrees/second
CycleTime = threshold/frequency # Amount of time it takes nodephase to get form 0 to 360 degrees

## Main Code ##
time1 = time.time() - (time.time() % CycleTime) # Time reference
Timer = 0
nodephase = 0

while True:

    try:
        ## Increasing the phase value ##
        Timer = time.time() - time1
        nodephase = heading + (Timer * frequency)

        ## Reaching the Threshold and Sending Pulses ##
        if nodephase >= threshold:
            time1 += CycleTime
            message = "T"
            Xbee.write(message.encode()) #Send the letter over the Xbee
            print("Pulse Sent")
            print("The phase value is: %f" % nodephase)

        ## Receiving Pulses and Adjusting Phase Value ##
        if Xbee.inWaiting() > 0: # If there is something in the receive buffer of the Xbee
            message = Xbee.read(Xbee.inWaiting()).decode() # Read all data in
            print(message) # To see what the message is
            if 0 < nodephase <= 180: # Adjusting nodephase based on heading
                heading -= nodephase/20
            if 180 < nodephase <= threshold: # Adjusting nodephase based on heading
                heading += (threshold - nodephase)/20
            if heading >= 360:
                heading -= 360
                time1 += CycleTime
                print("The heading is: %f" % heading)
            if heading <= 0:
                heading += 360
                time1 -= CycleTime
                print("The heading is: %f" % heading)
            print("The phase value is: %f" % nodephase)

        ## Recording Data ##


    ## Keyboard Interupt ##
    except KeyboardInterrupt:
        print('')
        break
    
    ## If the input is not a number ##
    except type(nodephase) == str:
        print("Please enter a number.")

## Ending Code ##
Xbee.close()

