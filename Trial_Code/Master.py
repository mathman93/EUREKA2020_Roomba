'''The master program that controls the simulations'''
#However, this does not mean that this is the master node, only that the program is the top-level program
#ALSO, I know that lots of this is hard coded, in this file and the PCO file, which in not the best way
#For the PCO file, its all about speed so that is why there (It could be MUCH smaller)
#For this file, its much easier to hard code, especially when these are the only tests running
#Verses trying to come up with all the logic to make sleaker, etc

import os
import time
import socket

#The file with all the PCO schemes coded
import PCO


#Prodecure
#1 - run all of one algoritom type before moving unto the next
#2 - store all possible testing parameters in lists BEFORE HAND so that no questions about what we be testing
    #^For starting phases, this info will be in a different file so that can be different for each pi
#3 - create all the file names and directories FIRST so that don't have to worry about losing radio communciation


#-------------------------------- Parameters --------------------------------
#Global
#refract_tests = [0, 0.01, 0.05, 0.1, 0.2] #IN SECONDS
refract_tests = [0]

#TODO - Read starting phases from file
#This file is a python list, located in the hostname folder with the name bellow
phase_path = os.path.join('/', 'home', 'pi', socket.gethostname(), 'start_phase.txt')
start_phase_tests = eval(open(phase_path).read())

#PERIOD currently at 2, however refract not really based on period
#delay_advance
#strength_tests = [0.1, 0.3, 0.5, 0.7, 0.9]
strength_tests = [0.7]
#perskin, M+S, Reachback
##epsilon_tests = [0.005, 0.01, 0.02, 0.05, 0.1, 0.3, 0.5] #Range 0 to 1
##epsilon_tests = [0.1] #Testing the b value
epsilon_tests = [0.005, 0.002, 0.001] #SPECICAL frb version
#NOTE, according to paper, when (number of nodes) * (epsilon) = optimal sync
#peskin
gamma_tests = [1, 3, 5, 8, 10] #Paper have at 1 and 3 -> try similar range
#M+S
b_tests = [1, 3, 5, 8, 10] #Paper have range 0+ to 10
#b_tests = [5] #Just testing epsilon


#-------------------------------- File Naming --------------------------------
#Prefix before files that tell what type it is AND name of respective directories for each type
delay_advance_perfix = 'da'
delay_advance_path = 'Delay_Advance'
perskin_perfix = 'prskn'
perskin_path = 'Perskin'
MS_perfix = 'ms'
MS_path = 'MirolloStrogatz'
Reachback_perfix = 'frb'
Reachback_path = 'FireflyReachback'

#-------------------------------- Type Dicts --------------------------------
#Creates dictonries that have all the information for the sim runner for each different sim type
#Then puts all the dicts in a list so that all the future operations can iterate through them
delay_advance_info = {'prefix':'da', #In file names that use this method
                      'direct':'Delay_Advance', #Directory name for all the tests
                      'parameters':[strength_tests, [False]], #Only including unique parameters
                      #use list with false so that can loop for both 3/4 parmeter functions w/o issue
                      'function': PCO.delay_advance
                      }
perskin_info = {'prefix':'prskn',
                'direct':'Perskin',
                'parameters':[epsilon_tests, gamma_tests],
                'function': PCO.peskin
                }
MS_info = {'prefix':'ms',
           'direct':'MirolloStrogatz',
           'parameters':[epsilon_tests, b_tests],
           'function': PCO.M_and_S
           }
Reachback_info = {'prefix':'frb',
                  'direct':'FireflyReachback',
                  'parameters':[epsilon_tests, [False]],
                  'function': PCO.Reachback_Firefly
                  }

method_dicts = [delay_advance_info, perskin_info, MS_info, Reachback_info]
##method_dicts = [delay_advance_info] #Only run DA for first tests
#If testing reachback, then help us all

#-------------------------------- File Setup --------------------------------
name = input('Directory name?') #Use custom name so that easier to get all direcotries
master_dir = socket.gethostname() + '_' + name
#Main directory for the trial that houses all the data and such

#Create the master_dir
base_path = os.path.join('/', 'home', 'pi', socket.gethostname(), master_dir) #CHANGE FOR PIS
os.mkdir(base_path)
#Creat child directories and 'key' files
for info in method_dicts:
    path = os.path.join(base_path, info['direct'])
    os.mkdir(path)
    #Key files are txt, which have name of each data file in directory AND its parameters
    keypath = os.path.join(path, info['prefix'] + '_key.txt')
    file = open(keypath, 'w', newline='')
    info['key'] = file
    info['path'] = path #The location to write the data files

#Testing to make sure for loops iterate correctly
#Level 1 - Different methods
##for info in method_dicts:
##    print('Starting ' + info['direct'] + ' tests')
##    #Level 2 - Start_phase
##    for start_phase in start_phase_tests:
##        #Level 3 - Refract
##        for refract in refract_tests:
##            #Level 4 - First unique parameter
##            for might in info['parameters'][0]:
##                #Level 5 - Second unique parameter
##                for constant in info['parameters'][1]:
##                    print('Calling ' + info['prefix'] + ' with these parameters:')
##                    print('Phase = ', start_phase)
##                    print('Refract = ', refract)
##                    print('Might = ', might)
##                    print('Constant = ', constant)
##                    print('------------------------------------------------------------------')



#The REAL DEAL Stuffs
#First call the start_sim to gets all the clocks synced up, then loop through conditions to collect data
MASTER = PCO.start_sim()
                    
#Level 1 - Different methods
for info in method_dicts:
    print('Starting ' + info['direct'] + ' tests')
    i = 0 #Counter that gives each file a unique number
    #Level 2 - Start_phase
    for start_phase in start_phase_tests:
        #Level 3 - Refract
        for refract in refract_tests:
            #Level 4 - First unique parameter
            for might in info['parameters'][0]:
                #Level 5 - Second unique parameter
                for constant in info['parameters'][1]:
                    head, f = info['function'](info['prefix']+str(i), info['path'], MASTER, start_phase, refract, might, constant)
                    head.insert(0, os.path.basename(f.name)) #Add filename to the list of info for the file
                    info['key'].write(str(head) + '\n') #Write info to file
                    i += 1 #Increment the counter

#Clean-up
#Close down all the key files AND Xbee
for info in method_dicts:
    info['key'].close()
PCO.Xbee.close()




