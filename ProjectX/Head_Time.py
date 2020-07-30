'''PCO that includes heading, SUPER EXPERIMENTAL'''
#You have been warned
#The idea is alternating periods of trying to adjust clock and heading
#The key is joinning the line at the right time (after hearing the line quiet for a full period


import csv
import time
import os
import serial
import socket
from random import uniform

#CONSTANTS
LOG_PERIOD = .01 #Time between when to log data
PERIOD = 4 #Time in seconds for each Ossilation
HALF_PERIOD = PERIOD/2
STRENGTH = .7 #Coe used with function to determine coupling strength?
REFRACT = 0 #Time before listen more signals
CONVERSION_FACTOR = (360.0 / PERIOD) #Multiply by the time in order to find degs FOR TIMER
CONVERSION_FACTOR_HALF = (360.0 / HALF_PERIOD) #Multiply by the time in order to find degs FOR HEADING
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
csvWriter.writerow(['Timestamp', 'HeadingPhase', 'Heading', 'HeadPing?', 'TimerPhase', 'TimerPing?'])

if ss: sync_start() #Try to set global time for all the nodes to start at
#----- END OF INIT -------


#------- BEGINNING PROCEDURES --------
#Variables that will be used during the MAIN LOOP

toWrite = [] #2D list that is temp storage for logs
heading = head #Used to store the 'heading' of an node -> only works with sync_start
timer_phase = 0
heading_phase = 0 #Header phase does not always exsits, only during small time between clock wait and pause
isheading_phase = False #True is the headering_phase is being updated / used
#Write intial conditions of osilator to file
toWrite.append([time.time(), heading_phase, heading, 0, timer_phase, 0])

#ABOVE HERE, SPEED IS NOT A CONCERN, HOWEVER GOING FORWARD IS SUPOSED TO BE FAST

timer_start = time.time() #The start time of the current cycle (for the timer)
heading_start = 0 #The start time for the heading cycle
PCO_start = start #The time the ossilator began
current_time = start #Used so that first interation of while loop works
log_timer = start + LOG_PERIOD #The time of the next periodic log
pinged = False #Used to store if the ossilator is supposed to ping this ossilation
offset = 0 #Bringing it back so that can have clock shifts
#-------- Main Loop ---------
while PCO_start + DURATION > current_time:
    try:
        #Update timer
        current_time = time.time()
        timer_phase = (current_time - timer_start) * CONVERSION_FACTOR_HALF + offset
        #Set heading phase
        if isheading_phase:
            heading_phase = ((current_time - heading_start) * CONVERSION_FACTOR_HALF + heading) % 360
            # % to keep in range 0-360

    #--------------Heading Stuff--------------
        
        #Check if need heading pulse based on if the heading phase
        #NOTE - this long calculation == heading_phase w/o the modulo operation
        if ((current_time - heading_start) * CONVERSION_FACTOR_HALF + heading) >= 360:
            #This is a heading pulse
            Xbee.write('h'.encode())
            #Write info
            toWrite.append([current_time, 360, heading, 1, timer_phase, 0])
            toWrite.append([current_time, 0, heading, 0, timer_phase, 0])

        #Check if need to stop the heading_phase from running
        if current_time - heading_start >= HALF_PERIOD:
            #Reset heading phase for the next time it is need and set isheading_phase to zero
            heading_phase = 0
            isheading_phase = False

    #--------------Timer Stuff--------------

        #Check if timer has reached the end of period
        if timer_phase >= 360:
            #Send timer pulse to other nodes (t) IF IT IS THE CORRECT CYCLE
            if pinged:
                Xbee.write('t'.encode())
            #Store both the top and bottom of a ping for better graphs
            toWrite.append([current_time, heading_phase, heading, 0, 360, 1])
            toWrite.append([current_time, heading_phase, heading, 0, 0, 0])
            #Then reset the timer and other things 
            timer_phase = 0
            timer_start = current_time
            log_timer = timer_start + LOG_PERIOD
            offset = 0
            #Flip its value so that next cycle is oposite (eg if pinged, don't)
            pinged = not pinged

        #Check if time to activate the heading_phase
        #This time is half way through the not pinging cycle
        if not pinged and current_time - timer_start >= HALF_PERIOD:
            #Kick on the heading stuff
            isheading_phase = True
            heading_phase = heading
            heading_start = current_time
            
    #--------------Phase Shift Stuff--------------

        #This is where it gets confusing, so lets break it down
        #3 - If during heading phase, then listen for heading signals and shift
        #1 - If during pause phase, then listen for clock signals and shift
        #2 - If during 'clock' phase, then don't do anything
            #b/c this could be a clock OR heading signal
        
        #Check for signals on the line
        inWait = Xbee.inWaiting()
        if inWait > 0:
            message = (Xbee.read(inWait)).decode()
            #Note - this will read all the pulses send to the serial port since the last
            #call of the loop, which maybe more than one. This is simply a risk that is taken
            #However, its exsistence is noted

            #Record the current phase before changing for good graphs
            toWrite.append([current_time, heading_phase, heading, 0, timer_phase, 0])

#-----PHASE RESPONSE PART------

            #Check for the different cases
            #1st - Heading period
            if isheading_phase:
                #Heading Phase Adjust
                '''
                Type = Delay-Advance
                Form = Wang Optimal Simple
                '''
                if heading_phase <= 180:
                    delta = STRENGTH * -heading_phase
                else:
                    delta = STRENGTH * (360 - heading_phase)
                heading += delta
                heading_phase += delta

            #2nd - Pause period
            elif pinged:
                #Clock Phase Adjust
                '''
                Type = Delay-Advance
                Form = Wang Optimal Simple
                '''
                if timer_phase <= 180:
                    delta = STRENGTH * -timer_phase
                else:
                    delta = STRENGTH * (360 - timer_phase)
                offset += delta
                timer_phase += delta

            #3rd - 'clock' period
            #Don't do anything

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


    
    






        
