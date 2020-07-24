import matplotlib.pyplot as plt
import numpy as np
import csv
import os
import glob

plt.ioff()


#Get file names
##x = os.listdir('Data_Files')
##print(x)
##filenames = []
##for name in x:
##    n = os.path.join('Data_Files',name)
##    if os.path.isdir(n):
##        ans = input('Want to Draw Contents of '+ name + ' ?')
##        if ans == 'y':
##            for file in glob.glob("Data_Files/"+name+"/*.csv"):
##                filenames.append(file)
##        elif ans == 'q':
##            break
##        else:
##            print('Not including')
##    elif os.path.isfile(n):
##        if os.path.splitext(name)[-1].lower() == '.csv':
##            ans = input('Want to Draw ' + name + ' ?')
##            if ans == 'y':
##                filenames.append(n)
##            elif ans == 'q':
##                break
##            else:
##                print('Not including')

filenames = []

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
                    if 0 <= int(index) <= len(possible_files)-1:
                        filenames.append(possible_files[int(index)])
                except:
                    print('Bad number, this is the end')
                    exit()
                    

print(filenames)
                     
colors = ['r', 'b', 'g', 'c', 'm', 'y']
i = 0
for fm in filenames:
    with open(fm, newline='') as f:
        reader = csv.reader(f, delimiter=',')
        x = []
        y = []
        for row in reader:
            try:
                x.append(float(row[0]))
                y.append(float(row[1]))
            except:
                print('Help')
            if row[3] == str(1):
                plt.plot(float(row[0]), float(row[1]), marker='o')
        plt.plot(x,y,colors[i])
        i += 1

plt.show()

