
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
epsilon = 0.1

while True:

    try:
        ## Increasing the phase value ##
        nodephase = (time.time() - time1) * 12

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
            x = (1/2) * (math.log1p((e**2 - 1) * nodephase))
            if 0 < x <= 3.5242:
                x -= epsilon
            if 3.524 < x < 3.8705:
                x += epsilon
            NodephasePlus = (e**(2 * x) - 1)/(e**2 - 1)
            time1 += NodephasePlus

    ## Keyboard Interupt ##
    except KeyboardInterrupt:
        print('')
        break
    
    ## If the input is not a number ##
    except type(nodephase) == str:
        print("Please enter a number.")

## Ending Code ##
Xbee.close()

