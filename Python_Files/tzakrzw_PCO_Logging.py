import time
import serial
import csv
import socket
from copy import copy
from random import uniform

#CONSTANT
LOG_PERIOD = .2 #Time between when to log data

#Function to adjust phase value
def wang_op_simple(self):
    if self.val <= self.period/2:
        return -self.val
    return self.period - self.val

#Object used to define the ossilator behavior
class Node():

    period = 1 #Time in seconds for each phase
    function = wang_op_simple #Function used to change phase value
    strength = 1 #Coe used with function to determine coupling strength?
    refract = .4 #Time before receive more signals

    def __init__(self, inital):
        self.val = inital #The value of the ossilator
                
    def phase(self): #Return phase value of node (Range 0-360) -> converted from time to deg
        return (self.val / self.period) * 360

    def pulse(self, ping=False): #Checks if the node is ready to pulse and then does it
        if self.val >= self.period:
            #Send out signal to other xbees
            Xbee.write(str(current_time).encode())
            #Reset value and set ping
            self.val = 0
            return 1
        return 0

    def change_phase(self): #Adjusts the phase_value based on rx pulses
        if self.val <= self.refract:
            return False
        #Use that value with the phase response equation to update end value
        self.val += self.strength * self.function()
        if self.val >= self.period:
            print('Over Shot')
            self.val = self.period
            self.pulse()
        elif self.val < 0:
            self.val = 360
            print('Negative shift')
        return True


# ---- Init ----
#Create ossilator
PCO = Node(uniform(0,Node.period)) #Just give a random intial phase

#Data file creation and such
fname = socket.gethostname() + '_' + time.strftime("%B %d, %Y, %H:%M:%S", time.gmtime()) + '.csv'
#That time format is stolen from Xbee_Read_Test ;)
file = open(fname, 'w', newline='')
csvWriter = csv.writer(file) #The object to write in csv format to the file
csvWriter.writerow(['Timestamp', 'Phase', 'Angle', 'Ping?'])
#Header for the file that defines what is in each column

toWrite = [] #2D list that is temp storage for logs
ping = 0 #Used to check if current cycle is a ping -> RESET BEFORE NEXT CYCLE

#Copy from Xbee_Read_Test.py to begin serial comunciation
global Xbee # Specifies connection to Xbee
Xbee = serial.Serial('/dev/ttyUSB0', 115200) # Baud rate should be 115200


# ---- Main Loop ----
last_time = time.time()
#Write intial conditions of osilator to file
csvWriter.writerow([last_time, PCO.phase(), 0, 0])
last_log = copy(last_time)
while True:
    try:
        current_time = time.time()
        dt = current_time - last_time #Change in time since last call
        PCO.val += dt #Update PCO value
        
        #Check to see if rx a pulse
        if Xbee.inWaiting() > 0:
            message = Xbee.read(Xbee.inWaiting()).decode()
            #Note - this will read all the pulses send to the serial port since the last
            #call of the loop, which maybe more than one. However, since their the refraction
            #period is greater than the time for a single loop to execute, this should be negliable
            PCO.change_phase()

        #Check nodes to see if an nodes need to fire
        ping = PCO.pulse()

        #Data Logging
        if current_time >= last_log + LOG_PERIOD:
            toWrite.append([current_time, PCO.phase(), 0, ping])
            last_log = copy(current_time)
        if ping == 1: #If we just pinged, then write the buffer to file
            #This is most likely during refractionary period, so we should be ok
            csvWriter.writerows(toWrite)
            toWrite = []
        
        #Finially, change the current_time to the last_time and print if ping
        last_time = copy(current_time)
        if ping == 1:
            print('Ping at' + str(current_time))

    except KeyboardInterrupt:
        print('This is the end')
        break

Xbee.close()
file.close()

    
    






        
