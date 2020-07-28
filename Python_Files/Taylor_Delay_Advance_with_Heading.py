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
time2 = 0
sendtimemin = 1
angle = 0 # Actual angle the robot is facing
heading = 0

while True:

    try:
        ## Increasing the phase value ##
        nodephase = heading + ((time.time() - time1) * 12)



        ## Reaching the Threshold and Sending Pulses ##
        if nodephase >= threshold:
            time1 = time.time()
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
            if 180 < nodephase < threshold:
                heading += (threshold - nodephase)/20
            print("The heading is: %f" % heading)
            if angle != heading:
                if heading > angle:
                    angle += heading/5
                    print("The angle is: %f" % angle)
                if heading < angle:
                    angle -= heading/5
                    print("The angle is: %f" % angle)
            if heading >= 360:
                heading = 0

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

