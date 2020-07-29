'''PCO that includes heading, Thomas edition'''
#Its gona get crazy, but lets do a thing and see if that works

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
STRENGTH = .7 #Coe used with function to determine coupling strength?
REFRACT = 0 #Time before listen more signals
CONVERSION_FACTOR = 360 / PERIOD #Multiply by the time in order to find degs
#eg value => phase OR seconds => degrees



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
                break
        while time.time() < start:
            pass
    print('Start')

# ---- Init ----

#Get some starting information
#This insures that all the files will have same name when trying to graph
file_sufix = input('Enter file sufix: ')
#Check if sync start wanted
if input('Sync start?'):
    ss = True
else:
    print('Note, skipping sync start/nHopefully, headings still sync')
    ss = False
#Set heading
try:
    head = float(input('Beginning Heading?'))
    if 0 <= head <= 360:
        pass
    else:
        raise ValueError('Out of acceptable range')
except:
    print('Giving random val')
    head = uniform(0,360)
#Set duration
try:
    DURATION = int(input('Duration? '))
except:
    print('Duration set to 20 secs')
    DURATION = 20

#Copy from Xbee_Read_Test.py to begin serial comunciation
global Xbee # Specifies connection to Xbee
Xbee = serial.Serial('/dev/ttyUSB0', 115200) # Baud rate should be 115200

#Data file creation and such
fname = socket.gethostname() + '_' + file_sufix + '.csv'
#Write files to non-github localtion on pis
path = os.path.join('..', '..', 'PCO_Data', fname)
file = open(path, 'w', newline='')
csvWriter = csv.writer(file) #The object to write in csv format to the file
#Header for the file that defines what is in each column
csvWriter.writerow(['Timestamp', 'Phase', 'Heading', 'Ping?'])

if ss: sync_start() #Try to set global time for all the nodes to start at
#----- END OF INIT -------


#------- BEGINNING PROCEDURES --------
#Variables that will be used during the MAIN LOOP
#NOTE - change from other versions -> there is no more 'value', only phase
#So all operations are now down in terms of degrees, not seconds OR parts of period

#NOTE - In this implentation, phase is the sum of heading and timer
#However, the phase can be greater than 360 and node still fires when phase = 360

toWrite = [] #2D list that is temp storage for logs
heading = head #Used to store the 'heading' of an node -> only works with sync_start
phase = heading #Set intial condition to head
#Write intial conditions of osilator to file
toWrite.append([time.time(), phase, heading, 0])

#ABOVE HERE, SPEED IS NOT A CONCERN, HOWEVER GOING FORWARD IS SUPOSED TO BE FAST

start = time.time() #The start time of the current cycle
PCO_start = start #The time the ossilator began
current_time = start #Used so that first interation of while loop works
log_timer = start + LOG_PERIOD #The time of the next periodic log
pinged = False #Used to store if the ossilator has pinged this ossilation
#-------- Main Loop ---------
while PCO_start + DURATION > current_time:
    try:
        #Update value
        current_time = time.time()
        phase = (current_time - start) * CONVERSION_FACTOR + heading #Set the phase
        #Remember to convert the time to phase equivalent (eg change from 0-PERIOD sec -> 0-360 deg)

        #Check if need to pulse and then send pulse
        if phase >= 360 and not pinged:
            Xbee.write(str(1).encode())
            #Write info
            #Store both the top and bottom of a ping for better graphs
            toWrite.append([current_time, 360, heading, 1])
            #THERE ARE NO RESETS as the resets happen when timer reaches 360
            pinged = True #So that PCO does not continiously ping


        #Check if timer has reached the end of period
        if current_time - start >= PERIOD:
            #Lets also ping here and see what happens
            Xbee.write(str(1).encode())
            #Store both the top and bottom of a ping for better graphs
            toWrite.append([current_time, phase, heading, 0])
            toWrite.append([current_time, 0, heading, 0])
            #Then reset the timer and phase
            phase = heading
            start = current_time
            log_timer = start + LOG_PERIOD
            pinged = False #Reset so that the ossilation can ping again
            #In order to keep heading restricted, subtract 360 if heading > 360
            if heading > 360:
                heading -= 360

        #Check for signals on the line -> if there is either end loop b/c synced
        #OR if not during refraction, then phase shift
        inWait = Xbee.inWaiting()
        if inWait > 0:
            Xbee.read(inWait)
            if current_time >= REFRACT + start:
                #Note - this will read all the pulses send to the serial port since the last
                #call of the loop, which maybe more than one. This is simply a risk that is taken
                #However, its exsistence is noted

                #Record the current phase before changing for good graphs
                toWrite.append([current_time, phase, heading, 0])
                
    #-----PHASE RESPONSE PART------
                '''
                Type = Delay-Advance
                Form = Wang Optimal Simple
                '''
                if phase > 360:
                    #Adjusting Heading
                    x = phase % 360 #Used in this implenation to calculate shifts
                    if x <= 180:
                        delta = STRENGTH * -x
                    else:
                        delta = STRENGTH * (360 - x)
                    heading += delta
                else:
                    #Adjusting timer
                    #Calculate deg to reaching maximum
                    x = (360 + heading) - phase
                    #x will always be less than 180 b/c phase requirements?
                    delta = STRENGTH * -x
                    timer += delta
                    
                phase += delta

    #-----END PHASE RESPONSE ------

                #Record the new phase
                toWrite.append([current_time, phase, heading, 0])
        
        #Periodic Data Logging
        if current_time >= log_timer:
            toWrite.append([current_time, phase, heading, 0])
            log_timer += LOG_PERIOD


    except KeyboardInterrupt:
        print('End Loop')
        break

print('Wait for file write')
csvWriter.writerows(toWrite)
if input('Wait to print out firing times and heading values?'):
    for line in toWrite:
        if line[3]:
            print(line[0], ' ', line[2])
if input('Keep Data?'):
    file.close()
Xbee.close()


    
    






        
