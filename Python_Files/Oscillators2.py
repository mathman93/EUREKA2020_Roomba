
## IMPORTANT ##
# The code involving the Xbees will be altered once I have access to the three Xbees and can distinguish between them in the code.
# For now, this code read like of all three oscillators are associated with the same Xbee, but this will be fixed later.

## Imports ##

import time
import serial


## Globals and Variables ##

global Xbee # Specifies connection to Xbee
Xbee = serial.Serial('/dev/ttyUSB0', 115200) # Baud rate should be 115200
#Starting phase angles of nodes 1, 2, and 3
nodephase1 = 100
nodephase2 = 200
nodephase3 = 300
threshold = 360
#Starting rate of change of the phase angles
nodephase1ROC = 5
nodephase2ROC = 5
nodephase3ROC = 5

## Main Code ##

while True:
    nodephase1 += nodephase1ROC
    nodephase2 += nodephase2ROC
    nodephase3 += nodephase3ROC
    
    ## Reaching the Threshold and Sending Pulses ##
    if nodephase1 == threshold:
        nodephase1 = 0
        message = "A"
        Xbee.write(message.encode()) #Send the letter over the Xbee
        print("Pulse Sent From Oscillator 1")
    if nodephase2 == threshold:
        nodephase2 = 0
        message = "B"
        Xbee.write(message.encode()) #Send the letter over the Xbee
        print("Pulse Sent From Oscillator 2")
    if nodephase3 == threshold:
        nodephase3 = 0
        message = "C"
        Xbee.write(message.encode()) #Send the letter over the Xbee
        print("Pulse Sent From Oscillator 3")

    ## Receiving Pulses and Adjusting Phase Value ##
    if Xbee.inWaiting() > 0: # If there is something in the receive buffer of the Xbee for oscillator 1
        message = Xbee.read(Xbee.inWaiting()).decode() # Read all data in
        print(message) # To see what the message is
        if 0 < nodephase1 <= 180:
            nodephase1 -= nodephase1ROC
        if 180 < nodephase1 < 360:
            nodephase1 += nodephase1ROC
    if Xbee.inWaiting() > 0: # If there is something in the receive buffer of the Xbee for oscillator 2
        message = Xbee.read(Xbee.inWaiting()).decode() # Read all data in
        print(message) # To see what the message is
        if 0 < nodephase2 <= 180:
            nodephase2 -= nodephase2ROC
        if 180 < nodephase1 < 360:
            nodephase2 += nodephase2ROC
    if Xbee.inWaiting() > 0: # If there is something in the receive buffer of the Xbee for oscillator 3
        message = Xbee.read(Xbee.inWaiting()).decode() # Read all data in
        print(message) # To see what the message is
        if 0 < nodephase3 <= 180:
            nodephase3 -= nodephase3ROC
        if 180 < nodephase3 < 360:
            nodephase3 += nodephase3ROC
    time.sleep(30)
