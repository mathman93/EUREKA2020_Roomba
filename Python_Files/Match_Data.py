'''Matches the data files from different raspberrypis based on conditions'''
import os
#Output is a file, which lists the realtive paths to files
#Past this to a plotter, which will graph the files given to it

#Ask for directories
dir_to_match = []
print('Select the directories that you want to be matched')
for hostname in os.listdir('Data_Files'):
    path = os.path.join('Data_Files', hostname)
    if 'z' not in hostname and os.path.isdir(path):
        #This is a folder with some good data
        #List out avalible directories inside and choice the one you want
        while True:
            print('Current directory: ', hostname)
            i = 0
            trials = os.listdir(path)
            for trial in trials:
                print(i, ' - ', trial)
                i += 1
            index = input('Select index of directory : ')
            try:
                if index == 'n': #If you want to skip a directory
                    break
                dir_to_match.append(os.path.join(path,trials[int(index)]))
                break
            except:
                print('Incorrect value, try again')

#Now find key files
#First layer: different dir
keys_to_match = []
for hostname_path in dir_to_match:
    #Go through the second layer (the different methods)
    for method_name in os.listdir(hostname_path):
        method_path = os.path.join(hostname_path, method_name)
        #Find the key file
        for file in os.listdir(method_path):
            if 'key' in file: #Don't need to check if a file b/c there are no dir here
                keys_to_match.append(os.path.join(method_path, file))

#Now time to match up the data in each of the key files
#the lines from each file should match up
linked = []
files = []
#Open all files
for file in keys_to_match:
    files.append(open(file))
#Loop through files untill read all lines
end = True
while end:
    current_link = [] #Add the matching pairs, triples to this
    for file in files:
        try:
            name = eval(file.readline())[0]
            current_link.append(name)
        except:
            print('End of file')
            end = False
            break
    linked.append(current_link)


for match in linked:
    print(match)














