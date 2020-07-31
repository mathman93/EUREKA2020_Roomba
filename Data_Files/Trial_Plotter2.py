'''Version 2.0, where we do lots of good stuff'''

import matplotlib.pyplot as plt
import numpy as np
import csv
import os
import glob

#Types of graphs and data
# 1 - Phase over time (the basics)
# 2 - Difference in Phase over time (both the average and the max)
# 2' - Difference in Phase over time once 'synced'
# 3 - Offset over time (this is in seconds!)
# 4 - File with data:
#       Number of cycles to sync, avg difference in phase once synced, and maybe other things


#Graphs phase over time
def graph_phase(filepaths):
    colors = ['r', 'b', 'g']
    i = 0
    for fm in filepaths:
        with open(fm, newline='') as f:
            reader = csv.reader(f, delimiter=',')
            x = []
            y = []
            for row in reader:
                try:
                    x.append(float(row[0]))
                    y.append(float(row[1]))
                except:
                    pass
                if row[3] == str(1):
                    plt.plot(float(row[0]), float(row[1]), marker='o')
            plt.plot(x,y,colors[i])
            i += 1

    plt.savefig(os.path.basename(filepaths[0]).replace('.csv', '') + 'phase.svg', bbox_inches='tight')
    plt.close()


#Graph Differences in Phase over time (minimum arc to contain all the phases)
def graph_difference(filepaths):
    #Theory, all recorded times should line up b/c sync start -> do not include non-periodic stuff
    #Now pull all the data from the files and sort out the non-periodic measurement stuff
    all_data = [] #3d list with all the data times and phases
    for file in filepaths:
        current_data = []
        with open(file, newline='') as f:
            reader = csv.reader(f, delimiter=',')
            #Read through all the peridoic measurement lines and record the time / phase
            for row in reader:
                try: #Because is try to read index 4 and it does not exsist
                    if row[4] == '42': #Indicator that this is periodic meaurement
                        current_data.append((row[0], row[1]))
                except:
                    pass #Non-periodic data
        all_data.append(current_data) #Put the data for this file in the all data list

    #Calculate the smallest arc for each recorded time
    arc_lengths = [] #Arc_length
    times = [] #Times
    for index in range(len(all_data[0])-10): # -5 to prevent weird stuff
        #Put the data for the same time in a list, which then used to calc stuff
        current_info = []
        for data in all_data:
            current_info.append(data[index]) #Add tuples that SHOULD have same time to the current_info
        times.append(float(current_info[0][0]))
        current_phases = []
        for i in range(len(current_info)):
            current_phases.append(float(current_info[i][1]))
        #Finally calculate all the constants and figue out the smallest
        #NOTE - this assumes three nodes
        current_phases.sort() #So that max is 2, min is 0, and middle is 1
        A = abs(360 - current_phases[2])
        B = float(current_phases[0])
        C = abs(current_phases[2] - current_phases[1])
        D = abs(current_phases[1] - current_phases[0])
        arc_lengths.append(min([D+C, A+B+C, A+B+D]))

    #Now, we can graph 
    plt.plot(times,arc_lengths,'r')

    plt.savefig(os.path.basename(filepaths[0]).replace('.csv', '') + 'diff.svg', bbox_inches='tight')
    plt.close()

#Graphs the offset over time
def graph_offset(filepaths):
    colors = ['r', 'b', 'g']
    i = 0
    for fm in filepaths:
        with open(fm, newline='') as f:
            reader = csv.reader(f, delimiter=',')
            x = []
            y = []
            for row in reader:
                try:
                    x.append(float(row[0]))
                    y.append(float(row[2]))
                except:
                    pass
            plt.plot(x,y,colors[i])
            i += 1

    plt.savefig(os.path.basename(filepaths[0]).replace('.csv', '') + 'offset.svg', bbox_inches='tight')
    plt.close()



plt.ioff()
#Give file path for all the datas that want to plot
rp1_path = os.path.join('raspberrypi1', 'raspberrypi1_128')
rp2_path = os.path.join('raspberrypi2', 'raspberrypi2_128')
rp3_path = os.path.join('raspberrypi3', 'raspberrypi3_128')

os.system('scp -r pi@192.168.1.14:' + rp1_path + ' raspberrypi1')
os.system('scp -r pi@192.168.1.15:' + rp2_path + ' raspberrypi2')
os.system('scp -r pi@192.168.1.17:' + rp3_path + ' raspberrypi3')

for directory in os.listdir(rp1_path):
    #Manually drill down into each directory and create seperate lists IN ORDER of the data
    #I know should be better, but I need to get this done
    rp1_Files = []
    rp1_Paths = []
    print(rp1_path)
    for file in glob.glob(rp1_path + '/' + directory + '/*.csv'):
        rp1_Paths.append(file)
        rp1_Files.append(os.path.basename(file))
    rp2_Files = []
    rp2_Paths = []
    for file in glob.glob(rp2_path + '/' + directory + '/*.csv'):
        rp2_Paths.append(file)
        rp2_Files.append(os.path.basename(file))
    rp3_Files = []
    rp3_Paths = []
    print(rp3_path)
    for file in glob.glob(rp3_path + '/' + directory + '/*.csv'):
        rp3_Paths.append(file)
        rp3_Files.append(os.path.basename(file))
    print(rp2_Paths)


    #Check to make sure all the same files
    if rp1_Files == rp2_Files == rp3_Files: 
        print('Matching files == good to go!!!')
    else:
        print('Files not match')
        exit()

    #Loop through all the files
    for j in range(len(rp1_Files)):
        print('Next file')
        filenames = [rp1_Paths[j], rp2_Paths[j], rp3_Paths[j]] 
        graph_phase(filenames)
        graph_difference(filenames)
        graph_offset(filenames)

