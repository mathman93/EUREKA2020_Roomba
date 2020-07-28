'''Striped down version of the PCO that should run faster'''

import csv
import time
import os
import serial
import socket
from random import uniform

#CONSTANTS
LOG_PERIOD = .01 #Time between when to log data
PERIOD = 2 #Time in seconds for each Ossilation
HALF_PERIOD = PERIOD/2
STRENGTH = .3 #Coe used with function to determine coupling strength?
REFRACT = 0 #Time before listen more signals




#SET UP MASTER LAST!!!!!!!!!!!
def sync_start(): #Used to sync the starting times of nodes
    if input('Master?'): #If input something, then master
        #It will send a pulse to other nodes of the start time of ossilation
        start_dt = input('Start When?')
        try:
            x = int(start_dt)
            start = int(time.time()) + x
            print('Starts in ' + str(start_dt))
            Xbee.write(str(start).encode())
            while time.time() < start:
                if Xbee.inWaiting() > 0:
                    message = str(Xbee.read(Xbee.inWaiting()).decode())
                    print(message + ' added')
        except:
            print('Count down failed')
            print('Starting w/o countdown')

    else: #Other nodes
        print('Waiting for master')
        while True:
            if Xbee.inWaiting() > 0:
                start = int(Xbee.read(Xbee.inWaiting()).decode())
                print('Start in ' + str(start - int(time.time())))
                Xbee.write(socket.gethostname().encode())
                break
        while time.time() < start:
            pass
    print('Start')

# ---- Init ----

#Get some starting information
#This insures that all the files will have same name when trying to graph
file_sufix = input('Enter file sufix: ')
if input('Sync start?'):
    ss = True
    #Set intial phase
    try:
        phs = float(input('Beginning Val? '))
        if REFRACT <= phs <= PERIOD:
            pass
        else:
            raise ValueError('Out of acceptable range')
    except:
        print('Giving random val')
        phs = uniform(REFRACT, PERIOD)
    #Set duration
    try:
        duration = int(input('Duration? '))
    except:
        print('Duration set to 30secs')
        DURATION = 30
else:
    print('Note, skipping Sync start might cause nodes not to sync based on refract length')
    phs = uniform(0,PERIOD)
    ss = False

#Copy from Xbee_Read_Test.py to begin serial comunciation
global Xbee # Specifies connection to Xbee
Xbee = serial.Serial('/dev/ttyUSB0', 115200) # Baud rate should be 115200

#Data file creation and such
fname = socket.gethostname() + '_' + file_sufix + '.csv'
#That time format is stolen from Xbee_Read_Test ;)
#Write files to non-github localtion on pis
path = os.path.join('..', '..', 'PCO_Data', fname)
file = open(path, 'w', newline='')
csvWriter = csv.writer(file) #The object to write in csv format to the file
#Header for the file that defines what is in each column
csvWriter.writerow(['Timestamp', 'Phase', 'Offset', 'Ping?'])

if ss: sync_start() #Try to set global time for all the nodes to start at
#----- END OF INIT -------


#------- BEGINNING PROCEDURES --------
#Variables that will be used during the MAIN LOOP

toWrite = [] #2D list that is temp storage for logs
value = 0 #The value of the ossilator, which used to find phase
offset = phs #The increase to value caused by phase shifts (or inital conditions)
head = 0 #Used to store the 'heading' of an node -> only works with sync_start
#Write intial conditions of osilator to file
toWrite.append([time.time(), phs / PERIOD * 360, 0, 0])

#ABOVE HERE, SPEED IS NOT A CONCERN, HOWEVER GOING FORWARD IS SUPOSED TO BE FAST

start = time.time() #The start time of the current cycle
PCO_start = start #The time the ossilator began
current_time = start #Used so that first interation of while loop works
log_timer = start + LOG_PERIOD #The time of the next periodic log
#-------- Main Loop ---------
while PCO_start + DURATION > current_time:
    try:
        #Update value
        current_time = time.time()
        value = current_time - start + offset #Set the value

        #Check if need to pulse and then send pulse
        if value >= PERIOD:
            Xbee.write(str(1).encode())
            #Write info
            #Store both the top and bottom of a ping for better graphs
            toWrite.append([current_time, 360, offset, 1])
            toWrite.append([current_time, 0, 0, 0])
            #Reset start, log_timer, offset, and value
            start = current_time
            log_timer = start + LOG_PERIOD
            head += offset #TESTING -> MAY LEAVE LATER
            offset = 0
            value = 0 #Insures that change_phase and log_timer work 


        #Check for signals on the line -> if there is either end loop b/c synced
        #OR if not during refraction, then phase shift
        inWait = Xbee.inWaiting()
        if inWait > 0:
            Xbee.read(inWait)
            if value >= REFRACT:
                #Note - this will read all the pulses send to the serial port since the last
                #call of the loop, which maybe more than one. This is simply a risk that is taken
                #However, its exsistence is noted

                #Record the current phase before changing for good graphs
                toWrite.append([current_time, (value / PERIOD) * 360, offset, 0])
                
    #-----PHASE RESPONSE PART------
                '''
                Type = Delay-Advance
                Form = Wang Optimal Simple
                '''
                if value <= HALF_PERIOD:
                    delta = STRENGTH * -value
                else:
                    delta = STRENGTH * (PERIOD - value)
                value += delta
                offset += delta

    #-----END PHASE RESPONSE ------

                #Record the new phase
                toWrite.append([current_time, (value / PERIOD) * 360, offset, 0])
        
        #Periodic Data Logging
        if current_time >= log_timer:
            toWrite.append([current_time, (value / PERIOD) * 360, offset, 0])
            log_timer += LOG_PERIOD


    except KeyboardInterrupt:
        print('End Loop')
        break

print('Wait for file write')
csvWriter.writerows(toWrite)
Xbee.close()
file.close()

    
    






        
