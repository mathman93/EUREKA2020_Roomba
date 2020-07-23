import matplotlib.pyplot as plt
import numpy as np
import csv
import os
import glob

plt.ion()


#Get file names
x = os.listdir('Data_Files')
print(x)
filenames = []
for name in x:
    n = os.path.join('Data_Files',name)
    if os.path.isdir(n):
        ans = input('Want to Draw Contents of '+ name + ' ?')
        if ans == 'y':
            for file in glob.glob("Data_Files/"+name+"/*.csv"):
                filenames.append(file)
        elif ans == 'q':
            break
        else:
            print('Not including')
    elif os.path.isfile(n):
        if os.path.splitext(name)[-1].lower() == '.csv':
            ans = input('Want to Draw ' + name + ' ?')
            if ans == 'y':
                filenames.append(n)
            elif ans == 'q':
                break
            else:
                print('Not including')


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

