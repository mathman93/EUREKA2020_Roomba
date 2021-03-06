
## IMPORTANT ##
# The code involving the Xbees will be altered once I have access to the three Xbees and can distinguish between them in the code.
# For now, this code read like of all three oscillators are associated with the same Xbee, but this will be fixed later.

## Imports ##

import time
import serial
import math

## Globals and Variables ##

global Xbee # Specifies connection to Xbee
Xbee = serial.Serial('/dev/ttyUSB0', 115200) # Baud rate should be 115200
#Starting phase angle
nodephase = int(input("Please enter a starting phase value: "))
threshold = 360

## Main Code ##
time1 = time.time()
sendtimemin = 1
epsilon = .9
ScalingFactor = 48

while True:

    try:
        ## Increasing the phase value ##
        nodephase = (time.time() - time1) * ScalingFactor

        ## Reaching the Threshold and Sending Pulses ##
        if nodephase >= threshold:
            time1 = time.time()
            message = "T"
            Xbee.write(message.encode()) #Send the letter over the Xbee
            print("Pulse Sent")
            print(nodephase)

        ## Receiving Pulses and Adjusting Phase Value ##
        if Xbee.inWaiting() > 0: # If there is something in the receive buffer of the Xbee for oscillator 1
            message = Xbee.read(Xbee.inWaiting()).decode() # Read all data in
            print(message) # To see what the message is
            print(nodephase)
            x = (360/2) * (math.log1p((math.expm1(2) * (nodephase/360))))
            x += epsilon
            NodephasePlus = 360 * ((math.expm1(2 * (x/360)))/(math.expm1(2)))
            if NodephasePlus > 360:
                nodephase = threshold
                message = "T"
                Xbee.write(message.encode())
                print("Pulse Sent")
            time1 -= (NodephasePlus - nodephase)/ScalingFactor

    ## Keyboard Interupt ##
    except KeyboardInterrupt:
        print('')
        break
    
    ## If the input is not a number ##
    except type(nodephase) == str:
        print("Please enter a number.")

## Ending Code ##
Xbee.close()

