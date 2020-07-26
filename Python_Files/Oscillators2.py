## Imports ##

import time
import serial

## Globals and Variables ##

global Xbee # Specifies connection to Xbee
Xbee = serial.Serial('/dev/ttyUSB0', 115200) # Baud rate should be 115200
#Starting phase angle
nodephase = int(input("Please enter a starting phase value: "))
threshold = 360

## Main Code ##
time1 = time.time()
sendtimemin = 1

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
            if 0 < nodephase <= 180:
                time1 += nodephase/20
            if 180 < nodephase < threshold:
                time1 -= nodephase/20

    ## Keyboard Interupt ##
    except KeyboardInterrupt:
        print('')
        break
    
    ## If the input is not a number ##
    except type(nodephase) == str:
        print("Please enter a number.")

## Ending Code ##
Xbee.close()
