'''Code for the different PCO (used during trails)'''
#Essentially wrappers that incorperate the main loops

import csv
import time
import os
import serial
import math
import socket
from copy import copy
from random import uniform

NODE_COUNT = 2 #Number of excpeted nodes on the network, if there are less, then retry to sync

#These bellow will be the same for all tests as they should not effect data
#HOWEVER, in the future might experiment with changing
LOG_PERIOD = .01 #Time between when to log data
PERIOD = 2 #Time in seconds for each Ossilation
HALF_PERIOD = PERIOD/2
SIM_LENGTH = 30 #Time in seconds that each trial runs for

#Start serial communciation when import this module, b/c can do it now and will always be avaible for all functions
global Xbee # Specifies connection to Xbee
Xbee = serial.Serial('/dev/ttyUSB0', 115200) # Baud rate should be 115200


#-------------------------------- General Start-Up Procedures --------------------------------


#Sets up files stuffs
def init_file(file_prefix, file_path, header):
    file_name = file_prefix + time.strftime("%I%p%M%S")
    path = os.path.join(file_path, file_name)
    file = open(path, 'w', newline='')
    csvWriter = csv.writer(file) #The object to write in csv format to the file
    csvWriter.writerow(header) #Tells what Parmameters / Algortium that was used for
    csvWriter.writerow(['Timestamp', 'Phase', 'Offset', 'Ping?']) #Defines what is in each column
    return csvWriter, file

#Used to syncronize the start of the ossilators
def sync_start(master):
    #In while loop so can restart if there is a problem
    while True:
        try:
            if master:
                nc = 1 #Count of how many nodes have registered for communication
                print('Wait for other nodes to prepare')
                time.sleep(5) #Wait for five seconds to give other nodes time to prepare to rx signals
                print('Sending start time for 5 seconds')
                start = int(time.time()) + 5
                Xbee.write(str(start).encode())
                while time.time() < start-2: #Do check with 2 seconds left to see if all the nodes are ready
                    if Xbee.inWaiting() > 0:
                        message = str(Xbee.read(Xbee.inWaiting()).decode())
                        print(message + ' added')
                        nc += 1
                #NOTE - still 2 seconds till start
                if nc != NODE_COUNT: #Check if everyone is here
                    Xbee.write('q'.encode()) #Send a quit signal to the other nodes
                    print('Not all nodes registered -> Canceled start time')
                    print('resending new start time')
                else: #If not then just resume the waiting loop
                    while time.time() < start:
                        pass
                    return start #All good to go and start
            
            else: #Other nodes, which are waiting for start time
                print('Waiting for master')
                skip = False
                while True:
                    if Xbee.inWaiting() > 0:
                        try: #This try/except is to handle if a quit signal is recieved before a time
                            start = int(Xbee.read(Xbee.inWaiting()).decode())
                        except:
                            print('Recieved quit before a start time -> restarting sync')
                            skip = True #Used to get out of the next while loop
                        print('Start in ' + str(start - int(time.time())))
                        Xbee.write(socket.gethostname().encode())
                        break
                if not skip: #Used to check if be got an error eariler and therefore should skip the next sync step
                    #Now wait for the start, while looking for a quit signal
                    while time.time() < start:
                        if Xbee.inWaiting() > 0:
                            Xbee.read(Xbee.inWaiting()) #This is most likely a quit, if not then still reset
                            print('Recieved a quit signal -> restarting sync')
                            skip = True #Used to cause a reset and not satify next conditional
                            break
                if not skip: #Final check
                    return start #All good to go and start

        #In case of a user reset to the syncs sequence:
        except KeyboardInterrupt:
            print('Restarting sync')
            print('Restart other nodes first so that they are ready to hear from master')

def start_sim():#Makes sure that all nodes are online before beginning simulations
    #Also, sets up which node is the master, then calls sync_start
    #AS ALWAYS, CALL THE MASTER LAST!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    master = input('Is master?')
    if master:
        sync_start(True)
        return True
    else:
        sync_start(False)
        return False


#-------------------------------- General End Procedures --------------------------------


def end(buffer, file, csvWriter): #Only really closes the file -> could do other things, I guess
    print('Wait for file write')
    csvWriter.writerows(buffer)
    file.close()


#-------------------------------- Type Specifc Prodeures --------------------------------
#To make running through the tests easier, each different method /algoritum will have 4 changing parameters
#For DA and FRB, these last parameters will be False, so nothing will happen

def delay_advance(file_prefix, file_path, master, start_phase, REFRACT, STRENGTH, foo=False): #Everyones favorite method
    #Test(able) parameters:
    #Strength, Start Phase, refract*
    #* -> actually, performace not hindered by having 0, so mostlikly will not test
    #Also, could test function used to calc shift, but would require total new function (speed concerns)


    #Create header
    typ = 'Type = DelayAdvance'
    function = 'Function = Wang Sync Simple'
    strength = 'Coupling Strength = ' + str(STRENGTH)
    refract = 'Refract = ' + str(REFRACT)
    start = 'Start_phase = ' + str(start_phase)
    header = [typ, function, refract, strength, start]


    #Call init functions
    csvWriter, file = init_file(file_prefix, file_path, header)
    loop_start = sync_start(master)
    

    #Mostly direct copy from PCO_reach_sync w/o try/except for keybaord interupt AND start_phase is range 0-360
        #vs range 0-PERIOD
    #ALSO, loop only runs for SIM_LENGTH, then it ends
    
    #------- BEGINNING PROCEDURES --------
    #Variables that will be used during the MAIN LOOP

    toWrite = [] #2D list that is temp storage for logs
    value = 0 #The value of the ossilator, which used to find phase
    offset = (start_phase/360) * PERIOD #The increase to value caused by phase shifts (or inital conditions)
    #Write intial conditions of osilator to file
    toWrite.append([time.time(), phs / PERIOD * 360, 0, 0])

    #ABOVE HERE, SPEED IS NOT A CONCERN, HOWEVER GOING FORWARD IS SUPOSED TO BE FAST

    start = time.time() #The start time of the current cycle
    log_timer = start + LOG_PERIOD #The time of the next periodic log
    #-------- Main Loop ---------
    while current_time < loop_start + SIM_LENGTH: #Keep running untill run about 30 seconds
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
    #-------- Main Loop End ---------


    #Ending Procedures
    end(toWrite, file, csvWriter)
    return header, file #So that this can be recorded to the 'key' file










def peskin(file_prefix, file_path, master, start_phase, REFRACT, EPSILON, GAMMA): #The OG
    #Test(able) parameters:
    #Epsilon, Gamma*, Start Phase, refract
    #* -> no idea how this effects performance, but it will be interesting to see

    #Create header
    typ = 'Type = Mirollor Strogatz (-ish)'
    function = 'Function = Peskin'
    refract = 'Refract =' + str(REFRACT)
    epsilon = 'Epsilon =' + str(EPSILON)
    gamma = 'Gamma =' + str(GAMMA)
    start = 'Start_phase =' + str(start_phase)
    header = [typ, function, refract, epsilon, gamma, start]

    #Call init functions
    C = math.expm1(-GAMMA) # = (e^-GAMMA - 1) which is common value in Peskin formula
    csvWriter, file = init_file(file_prefix, file_path, header)
    loop_start = sync_start(master)
    

    #Mostly direct copy from PCO_Peskin w/o try/except for keybaord interupt AND start_phase is range 0-360
        #vs range 0-PERIOD
    #ALSO, loop only runs for SIM_LENGTH, then it ends
    
    #------- BEGINNING PROCEDURES --------
    #Variables that will be used during the MAIN LOOP

    toWrite = [] #2D list that is temp storage for logs
    value = 0 #The value of the ossilator, which used to find phase
    offset = (start_phase/360) * PERIOD #The increase to value caused by phase shifts (or inital conditions)
    #Write intial conditions of osilator to file
    toWrite.append([time.time(), phs / PERIOD * 360, 0, 0])

    #ABOVE HERE, SPEED IS NOT A CONCERN, HOWEVER GOING FORWARD IS SUPOSED TO BE FAST

    start = time.time() #The start time of the current cycle
    log_timer = start + LOG_PERIOD #The time of the next periodic log
    #-------- Main Loop ---------
    while current_time < loop_start + SIM_LENGTH: #Keep running untill run about 30 seconds
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
                Type = Mirollor Strogatz (-ish)
                Form = Peskin
                '''
                old_v = value #Used to calc offset
                #Scale value to range 0-1 for calculations and then scale back at end
                f = C*math.expm1(-GAMMA*(value / PERIOD))
                value = (1/GAMMA)*math.log(C/(C+(f+EPSILON))) * PERIOD #Make sure to rescale to period
                if value > PERIOD: value = PERIOD
                offset += value - old_v

    #-----END PHASE RESPONSE ------

                #Record the new phase
                toWrite.append([current_time, (value / PERIOD) * 360, offset, 0])
        
        #Periodic Data Logging
        if current_time >= log_timer:
            toWrite.append([current_time, (value / PERIOD) * 360, offset, 0])
            log_timer += LOG_PERIOD
    #-------- Main Loop End ---------


    #Ending Procedures
    end(toWrite, file, csvWriter)
    return header, file #So that this can be recorded to the 'key' file









def M_and_S(file_prefix, file_path, master, start_phase, REFRACT, EPSILON, B): #The freqently cited, popularizer
    #Test(able) parameters:
    #Epsilon, B*, Start Phase, refract
    #* -> no idea how this effects performance, but it will be interesting to see

    #Create header
    typ = 'Type = Mirollor Strogatz (-ish)'
    function = 'Function = Mirollor Strogatz'
    refract = 'Refract = ' + str(REFRACT)
    epsilon = 'Epsilon = ' + str(EPSILON)
    b = 'B = ' + str(B)
    start = 'Start_phase = ' + str(start_phase)
    header = [typ, function, refract, epsilon, b, start]

    #Call init functions
    C = math.expm1(B) # = (e^B - 1) which is common value in M+S formula
    csvWriter, file = init_file(file_prefix, file_path, header)
    loop_start = sync_start(master)
    

    #Mostly direct copy from PCO_MS w/o try/except for keybaord interupt AND start_phase is range 0-360
        #vs range 0-PERIOD
    #ALSO, loop only runs for SIM_LENGTH, then it ends
    
    #------- BEGINNING PROCEDURES --------
    #Variables that will be used during the MAIN LOOP

    toWrite = [] #2D list that is temp storage for logs
    value = 0 #The value of the ossilator, which used to find phase
    offset = (start_phase/360) * PERIOD #The increase to value caused by phase shifts (or inital conditions)
    #Write intial conditions of osilator to file
    toWrite.append([time.time(), phs / PERIOD * 360, 0, 0])

    #ABOVE HERE, SPEED IS NOT A CONCERN, HOWEVER GOING FORWARD IS SUPOSED TO BE FAST

    start = time.time() #The start time of the current cycle
    log_timer = start + LOG_PERIOD #The time of the next periodic log
    #-------- Main Loop ---------
    while current_time < loop_start + SIM_LENGTH: #Keep running untill run about 30 seconds
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
                Type = Mirollor Strogatz (-ish)
                Form = Mirrolo and Strogatz
                '''
                old_v = value #Used to calc offset
                #Scale value to range 0-1 for calculations and then scale back at end
                f = (1/B)*math.log(1+C*(value / PERIOD))
                value = math.expm1((f+EPSILON)*B)/C * PERIOD #Make sure to rescale to period
                if value > PERIOD: value = PERIOD
                offset += value - old_v

    #-----END PHASE RESPONSE ------

                #Record the new phase
                toWrite.append([current_time, (value / PERIOD) * 360, offset, 0])
        
        #Periodic Data Logging
        if current_time >= log_timer:
            toWrite.append([current_time, (value / PERIOD) * 360, offset, 0])
            log_timer += LOG_PERIOD
    #-------- Main Loop End ---------


    #Ending Procedures
    end(toWrite, file, csvWriter)
    return header, file #So that this can be recorded to the 'key' file



        





def Reachback_Firefly(file_prefix, file_path, master, start_phase, REFRACT, EPSILON, foo=False): #By far, the worst
#Like, honestly who thought that this was a good idea -> maybe for practical applications
#But even then it is MUCH worse than than delay_advance as far as time to sync
#It has the worst retention of phase synconization
#And, its formula for sync is just plane lazy and therefore extremely inefcient
#And, in its 'Ground Breaking' paper, all the nodes use a different time syconizize algoritm IN ORDER TO IMPLENTMENT
#THE PCO MODEL -> what is the point of testing a new clock sync method IF you use an already exsting method to
#implenent it? Why, I ask you. While, I will write the code for this, however this method just overall if garbage.
#The main problems it seeked to solve (ie prevent avaliances of nodes fireing near the same time and ruinning an
#system from syncing) is well fixed by delay advance algortiums OR by just having an aproprite refractory period
#WHICH this implentation also calls for. I have no idea what benefit in todays PCO world this algoritum adds, but
#I will test it anyway just to show how TERRIBLE it is.

    #Test(able) parameters:
    #Epsilon, B*, Start Phase, refract
    #* -> no idea how this effects performance, but it will be interesting to see

    #Create header
    typ = 'Type = Reachback Firefly'
    function = 'Function = Reachback Firefly (ln/e^)'
    refract = 'Refract = ' + str(REFRACT)
    epsilon = 'Epsilon = ' + str(EPSILON)
    start = 'Start_phase = ' + str(start_phase)
    header = [typ, function, refract, epsilon, start]

    #Call init functions
    csvWriter, file = init_file(file_prefix, file_path, header)
    loop_start = sync_start(master)
    

    #Mostly direct copy from PCO_ReachFire w/o try/except for keybaord interupt AND start_phase is range 0-360
        #vs range 0-PERIOD
    #ALSO, loop only runs for SIM_LENGTH, then it ends
    
    #------- BEGINNING PROCEDURES --------
    #Variables that will be used during the MAIN LOOP

    toWrite = [] #2D list that is temp storage for logs
    value = 0 #The value of the ossilator, which used to find phase
    offset = (start_phase/360) * PERIOD #The increase to value caused by phase shifts (or inital conditions)
    next_offset = 0 #Stores the offset value for the next cycle
    #Write intial conditions of osilator to file
    toWrite.append([time.time(), phs / PERIOD * 360, 0, 0])

    #ABOVE HERE, SPEED IS NOT A CONCERN, HOWEVER GOING FORWARD IS SUPOSED TO BE FAST

    start = time.time() #The start time of the current cycle
    log_timer = start + LOG_PERIOD #The time of the next periodic log
    #-------- Main Loop ---------
    while current_time < loop_start + SIM_LENGTH: #Keep running untill run about 30 seconds
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
            offset = copy(next_offset) #Set the new offset value to that which had acumlated over the last cycle
            #Note - actually, all the calculations to find the next_offset should happen right now b/c
            #This time is during a refraction period, so even if there was an incoming single, PCO would not care
            #However, doing calc when get signle is still fast enough, as it is not really the bottleneck in the
            #loop (serial functions are)
            value = copy(next_offset) #Insures that change_phase and log_timer work
            next_offset = 0 #We do have to reset this to 0


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
                Type = Reachback Firefly
                Form = Reachback Firefly (Only version)
                '''
                #Scale value to range 0-1 for calculations and then scale back at end
                f = math.log(value/PERIOD)
                new_v = math.exp(f+EPSILON) * PERIOD #Make sure to rescale to period
                next_offset += new_v - value

    #-----END PHASE RESPONSE ------

                #Record the new phase
                toWrite.append([current_time, (value / PERIOD) * 360, offset, 0])
        
        #Periodic Data Logging
        if current_time >= log_timer:
            toWrite.append([current_time, (value / PERIOD) * 360, offset, 0])
            log_timer += LOG_PERIOD
    #-------- Main Loop End ---------


    #Ending Procedures
    end(toWrite, file, csvWriter)
    return header, file #So that this can be recorded to the 'key' file
