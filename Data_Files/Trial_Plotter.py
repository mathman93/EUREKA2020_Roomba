import matplotlib.pyplot as plt
import numpy as np
import csv
import os
import glob

plt.ioff()
#Give file path for all the datas that want to plot
rp1_path = os.path.join('raspberrypi1', 'raspberrypi1_Jul27_12PM39', 'FireflyReachback')
rp2_path = os.path.join('raspberrypi2', 'raspberrypi2_Jul27_12PM39', 'FireflyReachback')
#Manually drill down into each directory and create seperate lists IN ORDER of the data
#I know should be better, but I need to get this done
rp1_Files = []
rp1_Paths = []
for file in glob.glob(rp1_path + '/*.csv'):
    rp1_Paths.append(file)
    rp1_Files.append(os.path.basename(file))
rp2_Files = []
rp2_Paths = []
for file in glob.glob(rp2_path + '/*.csv'):
    rp2_Paths.append(file)
    rp2_Files.append(os.path.basename(file))

#Check to make sure all the same files
if rp1_Files == rp2_Files:
    print('Matching files == good to go!!!')
else:
    print('Files not match')
    exit()

#Loop through all the files
for j in range(len(rp1_Files)):
    filenames = [rp1_Paths[j], rp2_Paths[j]]
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

    plt.savefig(rp1_Files[j] + '.pdf', bbox_inches='tight')
    plt.close()
##    plt.show()

