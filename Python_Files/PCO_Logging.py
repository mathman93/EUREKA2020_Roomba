import csv
import time
import os
import serial
import socket
from copy import copy
from random import uniform

#Function to adjust phase value
def wang_op_simple(self):
    if self.val <= PERIOD/2:
        return -self.val
    return PERIOD - self.val

#CONSTANT
LOG_PERIOD = .01 #Time between when to log data
PERIOD = 5 #Time in seconds for each Ossilation
STRENGTH = .3 #Coe used with function to determine coupling strength?
REFRACT = .1 #Time before listen more signals
FUNCTION = wang_op_simple #Function used to change phase value

#SET UP MASTER LAST!!!!!!!!!!!
def sync_start(): #Used to sync the starting times of nodes
    if input('Master?'): #If input something, then master
        #It will send a pulse to other nodes of the start time of ossilation
        start_dt = input('Start When?')
        try:
            x = int(start_dt)
            start = int(time.time()) + x
            print('Starts in ' + str(start_dt))
            Xbee.write(x)
            while time.time() > start:
                if Xbee.inWaiting() > 0:
                    message = Xbee.read(Xbee.inWaiting()).decode()
                    print(message + ' added')
        except:
            print('Count down failed')
            print('Starting w/o countdown')

    else: #Other nodes
        print('Waiting for master')
        while True:
            if Xbee.inWaiting() > 0:
                message = Xbee.read(Xbee.inWaiting()).decode()
                print('Start in ' + str(start - int(time.time())))
                Xbee.write(socket.gethostname())
                break
        while time.time() > start:
            pass

PCO, toWrite, csvWriter = [None]*3

'''Timestamp, Phase, Angle, Ping?'''
def record(l_phase, force=False, n=PCO, toW=toWrite, W=csvWriter):
    #1 - Record if just pinged
    if n.ping:
        #Store both the top and bottom of a ping for better graphs
        toW.append([current_time, 360, 0, 1])
        toW.append([current_time, 0, 0, 0])
        
        #Also, write all the buffer to the file, mostlikely during refraction
        W.writerows(toW)
        
    #2 - Record if have a phase change
    elif l_phase: #This value will be the old phase if there was a phase change
        toW.append([current_time, l_phase, 0, 0])
        toW.append([current_time, n.phase(), 0, 0])
        
    #3 - Periodic Recording (Also can force record by passing True
    elif current_time >= n.last_log + LOG_PERIOD or force == True:
        toW.append([current_time, l_phase, 0, 0])
        n.last_log = copy(current_time)
        

#Object used to define the ossilator behavior
class Node():

    def __init__(self, inital):
        self.val = inital #The value of the ossilator
        self.ping = False #Store if the node just pinged
        self.last_log = None #Store time of last periodic record
                
    def phase(self): #Return phase value of node (Range 0-360) -> converted from time to deg
        return (self.val / PERIOD) * 360

    def pulse(self): #Checks if the node is ready to pulse and then does it
        if self.val >= PERIOD:
            #Reset value and set ping
            self.val = 0
            self.ping = True
            return True
        return False

    def change_phase(self): #Adjusts the phase_value
        lp = self.phase()
        #Use strength AND phase response equation to update value
        self.val += self.strength * self.function()
        #Checks to make sure value is within range
        if self.val > self.period: self.val = copy(PERIOD)
        elif self.val < 0: self.val = 0
        return lp #Used for data_logging


# ---- Init ----

#Copy from Xbee_Read_Test.py to begin serial comunciation
global Xbee # Specifies connection to Xbee
Xbee = serial.Serial('/dev/ttyUSB0', 115200) # Baud rate should be 115200

#Get some starting information
if input('Sync start?'):
    ss = True
    try:
        phs = int(input('Beginning Val?'))
        if REFRACT >= phs >= PERIOD:
            pass
        else:
            raise ValueError('Out of acceptable range')
    except:
        print('Giving random val')
        phs = uniform(REFRACT, PERIOD)
else:
    print('Note, skipping Sync start might cause nodes not to sync based on refract length')
    phs = uniform(0,PERIOD)
    ss = False

#Create ossilator
PCO = Node(phs)

#Data file creation and such
fname = socket.gethostname() + '_' + time.strftime("%B %d, %Y, %H:%M:%S", time.gmtime()) + '.csv'
#That time format is stolen from Xbee_Read_Test ;)
path = os.path.join('..', 'Data_Files', fname)
file = open(path, 'w', newline='')
csvWriter = csv.writer(file) #The object to write in csv format to the file
csvWriter.writerow(['Timestamp', 'Phase', 'Angle', 'Ping?'])
#Header for the file that defines what is in each column

toWrite = [] #2D list that is temp storage for logs


if ss: sync_start() #Try to set global time for all the nodes to start at

#Set up the time variables
last_time = time.time()
current_time = copy(last_time)

#Write intial conditions of osilator to file
record(None, force=True)

# ---- Main Loop ----
while True:
    try:
        current_time = time.time()
        dt = current_time - last_time #Change in time since last call
        PCO.val += dt #Update value

        #Check if need to pulse and then send pulse
        if PCO.pulse():
            Xbee.write(str(1).encode())

        #Check first if not during refractionary period and then if there is singals waiting
        if PCO.val > REFRACT: 
            if Xbee.inWaiting() > 0:
                message = Xbee.read(Xbee.inWaiting()).decode()
                #Note - this will read all the pulses send to the serial port since the last
                #call of the loop, which maybe more than one. However, since their the refraction
                #period is greater than the time for a single loop to execute, this should be negliable
                last_phase = PCO.change_phase()
        
        #Data Logging
        record(last_phase)

        #Clean-up and reset for next iteration
        last_time = copy(current_time)
        last_phase = None
        PCO.ping = False

    except KeyboardInterrupt:
        print('This is the end')
        break

Xbee.close()
file.close()

    
    






        
