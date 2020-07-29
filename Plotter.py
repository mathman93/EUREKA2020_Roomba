import matplotlib.pyplot as plt
import numpy as np
import csv
import os
import glob

plt.ioff()
old_way = False
filenames = []

#Pull down files from the pis
if input('Want to pull info down from pis? ') == 'y':
    os.system('scp -r pi@192.168.1.14:PCO_Data Data_Files/raspberrypi1')
    os.system('scp -r pi@192.168.1.15:PCO_Data Data_Files/raspberrypi2')
    os.system('scp -r pi@192.168.1.17:PCO_Data Data_Files/raspberrypi3')
#CHANGE SO THAT ALL MATCHING FILES HAVE SAME ENDINGS

#Basicly, look at the PCO_data folder of an pi and determine when sufix file to
#graph
#Can opt out by typeing 'old' on first question
x = input("Which pi's to look at? ")
if x == 'old':
    old_way = True
elif x in ['1', '2', '3']:
    #The directory to look at for all the files
    path = os.path.join('Data_Files', 'raspberrypi' + x, 'PCO_Data')
    #create list of sufixes
    suffixes = []
    for file in os.listdir(path):
        suffixes.append(file.split('_')[-1])
    suffixes.sort()
    #Search for file suffixes either from index OR by name
    while True:
        if input('Search by suffix? ') == 'y':
            #Searxh for suffix by name
            x = input('Enter suffix: ')
            if x in suffixes:
                print('Found suffix, getting data and graphing')
                file_suffix = x
                break
            else:
                print('Invalid, try another suffix or search by index')
        else:
            #Choice which sufix from the list
            i = 0
            for suffix in suffixes:
                print(i, ' - ', suffix)
                i += 1
            index = input('Choice index of the one you want ')
            try:
                if 0 <= int(index) <= len(suffixes)-1:
                    print('Found suffix, getting data and graphing')
                    file_suffix = suffixes[int(index)]
                    break
                else:
                    print('Invalid, try another index or search by suffix')
            except:
                print('Invalid, try another index or search by suffix')

    #Get the files and add path names to filenames
    for pi_num in ['1', '2', '3']:
        p = os.path.join('Data_Files', 'raspberrypi' + pi_num, 'PCO_Data',
                         'raspberrypi' + pi_num + '_' + file_suffix)
        if os.path.exists(p):
            filenames.append(p)







#Keep old functionality for odd cases
if old_way == True:
    ans = input('Get most recent? ')
    x = os.listdir('Data_Files')
    if ans == 'y':
        #Find the most recent files in each non-y containing directory
        for name in x:
            possible_files = []
            path = os.path.join('Data_Files',name)
            #Check if directory
            if os.path.isdir(path):
                #Check if contains a y
                if 'z' not in name:
                    #Look at all the files in the directory that are .csv
                    for file in glob.glob(path+"/**/*.csv", recursive=True):
                        #print(file)
                        possible_files.append(file)
                    #Then, cycle through and find the one with the largest number
                    greatest = '0'
                    great_path = None
                    for file in possible_files:
                        #Very dirty, put should work
                        fname = os.path.basename(file)
                        num = []
                        for char in fname:
                            try:
                                int(char) #check if number
                                num.append(char)
                                #print('new number ', char)
                            except:
                                continue
                        q = ''.join(num)
                        #print(q)
                        if int(q) > int(greatest):
                            greatest = int(q)
                            great_path = file
                    filenames.append(great_path)
        print(filenames)
        ans = input('Are these the files you are looking for? ')
    if ans != 'y':
        filenames = []
        print('ok, lets do this differently')
        print('pick you favorite files from each folder')
        for name in x:
            possible_files = []
            path = os.path.join('Data_Files',name)
            if os.path.isdir(path):
                #Check if contains a y
                if 'z' not in name:
                    for file in glob.glob(path+"/PCO_Data/*.csv"):
                        possible_files.append(file)
                    #Choice which file from the list
                    print('Directory: ', name)
                    i = 0
                    for file in possible_files:
                        print(i, ' - ', os.path.basename(file))
                        i += 1
                    index = input('Choice index of the one you want ')
                    try:
                        if index == 'n':
                            print('skipping directory')
                        elif 0 <= int(index) <= len(possible_files)-1:
                            filenames.append(possible_files[int(index)])
                    except:
                        print('Bad number, this is the end')
                        exit()
                    

print(filenames)
                     
colors = ['r', 'b', 'y', 'c', 'm', 'g']
i = 0
for fm in filenames:
    if fm:
        with open(fm, newline='') as f:
            reader = csv.reader(f, delimiter=',')
            x = []
            y = []
            for row in reader:
                try:
                    x.append(float(row[0]))
                    y.append(float(row[4]))
                except:
                    print('Help')
                #Graph phase value
                if row[3] == str(1):
                    plt.plot(float(row[0]), float(row[1]), marker='o', color='g')
                #Graph timer pulses
                try:
                    if row[5] == str(1):
                        plt.plot(float(row[0]), float(row[4]), marker='o', color='m')
                except:
                    pass
            plt.plot(x,y,colors[i])
            i += 1

plt.show()

