## Imports ##

import time
import serial

## Globals and Variables ##

global Xbee # Specifies connection to Xbee
Xbee = serial.Serial('/dev/ttyUSB0', 115200) # Baud rate should be 115200
#Starting phase angle
heading = int(input("Please enter your heading: "))
threshold = 360
frequency = 12
CycleTime = 30

## Main Code ##
Time1 = 0
OldTime = time.time() - (time.time() % CycleTime)
heading = 0
nodephase = 0

while True:

    try:
        ## Increasing the phase value ##
        NewTime = time.time()
        Time1 = NewTime - OldTime
        nodephase = heading + (Time1 * frequency)

        ## Reaching the Threshold and Sending Pulses ##
        if nodephase >= threshold:
            Time1 -= CycleTime
            OldTime = time.time() - (time.time() % CycleTime)
            message = "T"
            Xbee.write(message.encode()) #Send the letter over the Xbee
            print("Pulse Sent")
            print("The phase value is: %f" % nodephase)

        ## Receiving Pulses and Adjusting Phase Value ##
        if Xbee.inWaiting() > 0: # If there is something in the receive buffer of the Xbee for oscillator 1
            message = Xbee.read(Xbee.inWaiting()).decode() # Read all data in
            print(message) # To see what the message is
            print("The phase value is: %f" % nodephase)
            if 0 < nodephase <= 180:
                heading -= nodephase/20
            if 180 < nodephase <+ threshold:
                heading += (threshold - nodephase)/20
            if heading >= 360:
                heading -= 360
                Time1 += CycleTime
                print("The heading is: %f" % heading)
            if heading <= 0:
                heading += 360
                Time1 -= CycleTime
                print("The heading is: %f" % heading)
        
    ## Adjusting Angle to Get Closer to Heading ##


    ## Keyboard Interupt ##
    except KeyboardInterrupt:
        print('')
        break
    
    ## If the input is not a number ##
    except type(nodephase) == str:
        print("Please enter a number.")

## Ending Code ##
Xbee.close()

