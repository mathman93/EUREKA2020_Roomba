'''PCO that includes heading, my turn'''
#We got 2 channels / ossialtiors in one that lets everyone sync up
#Heading is controlled by one type of single (h)
#Timer is controlled by another single (t)
#Heading cycle start / end are based on Timer values



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
CONVERSION_FACTOR = (360.0 / PERIOD) #Multiply by the time in order to find degs
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
        while time.time() < start: #Keep the buffer empty
            if Xbee.inWaiting() > 0:
                Xbee.read(Xbee.inWaiting())
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
csvWriter.writerow(['Timestamp', 'HeadingPhase', 'Heading', 'HeadPing?', 'TimerPhase', 'TimerPing?'])

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
timer_phase = 0
heading_phase = timer_phase + heading
#Write intial conditions of osilator to file
toWrite.append([time.time(), heading_phase, heading, 0, timer_phase, 0])

#ABOVE HERE, SPEED IS NOT A CONCERN, HOWEVER GOING FORWARD IS SUPOSED TO BE FAST

start = time.time() #The start time of the current cycle
PCO_start = start #The time the ossilator began
current_time = start #Used so that first interation of while loop works
log_timer = start + LOG_PERIOD #The time of the next periodic log
pinged = False #Used to store if the ossilator has pinged this ossilation
offset = 0 #Bringing it back so that can have clock shifts
#-------- Main Loop ---------
while PCO_start + DURATION > current_time:
    try:
        #Update timer
        current_time = time.time()
        timer_phase = (current_time - start) * CONVERSION_FACTOR + offset
        #Set heading phase as function of timer_phase
        heading_phase = (timer_phase + heading) % 360  #To keep in range 0-360
        #Remember to convert the time to phase equivalent (eg change from 0-PERIOD sec -> 0-360 deg)

        #Check if need heading pulse based on if the heading phase (w/o %) is large enough
        if timer_phase + heading >= 360 and not pinged:
            #This is a heading pulse
            Xbee.write('h'.encode())
            #Write info
            toWrite.append([current_time, heading_phase, heading, 1, timer_phase, 0])
            #Modulo operator will take care of the resseting phase
            pinged = True #So that PCO does not continiously ping


        #Check if timer has reached the end of period
        if timer_phase >= 360:
            #Send timer pulse to other nodes (t)
            Xbee.write('t'.encode())
            #Store both the top and bottom of a ping for better graphs
            toWrite.append([current_time, heading_phase, heading, 0, 360, 1])
            toWrite.append([current_time, heading, heading, 0, 0, 0])
            #Then reset the timer and phases
            timer_phase = 0
            heading_phase = (timer_phase + heading) % 360
            start = current_time
            log_timer = start + LOG_PERIOD
            offset = 0
            pinged = False #Reset so that the ossilation can ping again
            #In order to keep heading restricted, subtract 360 if heading > 360
            if heading > 360:
                heading -= 360
            if heading < 0:
                heading += 360

        #Check for signals on the line -> if there is either end loop b/c synced
        #OR if not during refraction, then phase shift
        inWait = Xbee.inWaiting()
        if inWait > 0:
            message = (Xbee.read(inWait)).decode()
            if current_time >= REFRACT + start:
                #Note - this will read all the pulses send to the serial port since the last
                #call of the loop, which maybe more than one. This is simply a risk that is taken
                #However, its exsistence is noted

                #Record the current phase before changing for good graphs
                toWrite.append([current_time, heading_phase, heading, 0, timer_phase, 0])

                #Check if message contains 't' -> adjust timer
                #This will acount if have multiple signals of different types on the line
                #And default to timer sync, as that is more important
                if 't' in message:
                #Have phase response adjust timer value, like heading not exsist
                    if timer_phase <= 180:
                        delta = STRENGTH * -timer_phase
                    else:
                        delta = STRENGTH * (360 - timer_phase)
                    offset += delta
                    timer_phase += delta
                    heading_phase = (timer_phase + heading) % 360

                else:
                    #Just adjust the heading as you would normally
    #-----PHASE RESPONSE PART------
                    '''
                    Type = Delay-Advance
                    Form = Wang Optimal Simple
                    '''
                    if heading_phase <= 180:
                        delta = STRENGTH * -heading_phase
                    else:
                        delta = STRENGTH * (360 - heading_phase)
                    heading += delta
                    heading_phase = (timer_phase + heading) % 360

    #-----END PHASE RESPONSE ------

                #Record the new phase
                toWrite.append([current_time, heading_phase, heading, 0, timer_phase, 0])
        
        #Periodic Data Logging
        if current_time >= log_timer:
            toWrite.append([current_time, heading_phase, heading, 0, timer_phase, 0])
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
Xbee.close()


    
    






        
