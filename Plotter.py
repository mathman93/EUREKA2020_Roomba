import matplotlib.pyplot as plt
import numpy as np
import csv
import os

plt.ion()

filenames = ['raspberrypi1_July 21, 2020, 22:59:35.csv',
             'raspberrypi2_July 21, 2020, 22:59:51.csv']
#filenames = ['Node1.csv']
colors = ['r', 'b', 'g', 'c', 'm', 'y']
i = 0
for fm in filenames:
    with open(os.path.join('Data_Files', fm), newline='') as f:
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

