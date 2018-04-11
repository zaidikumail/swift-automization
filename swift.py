#!/usr/bin/python3
import subprocess, os, re

inputFile = open('swift.txt')                   #open the swift file    
lineNum = 0                                     #initialize the line count
attributes = []                                 #initializing the array to hold the location of the observation directories given by swift

for line in inputFile.readlines():              #loop to record the information from the file in 'attributes'
        line = line.strip('\n\r')
        attributes.append(line)
        lineNum += 1
inputFile.close()

if (os.path.exists(attributes[0])):             #the zeroth element of attributes is the first line of swift.txt
        array = (os.listdir(attributes[1]))     #array holds the foldernames in the observation directory
        mode = array[2]                         #mode holds the appropriate foldername in the observation directory to look for observation mode used
        PC = re.search('pc',mode, re.M|re.I)    #uses re to search for the 'pc' or 'wt' in the appropriate foldername to decide the mode of the observation
        WT = re.search('wt',mode, re.M|re.I)
        if PC:
                print('PC mode')
        elif WT:
                print('WT mode')
else:
        print('Observation not found')

line2 = attributes[1]
line2 = line2.split('/')
print(line2)
line2.reverse()
print(line2)
obsid = line2[2] 
print('ObsID: ' + obsid)
indir = './' + line2[3] + '/' + obsid 	#3 and 4 correspond to the 3rd and 4th elements separated by '/' in swift.txt line 1
print('indir:' + indir)
steminputs = 'sw' + obsid
print('steminputs: ' + steminputs)
outdir = './' + obsid + '-xrt'
print('outdir: ' + outdir) 
xrt = "xrtpipeline indir=" + indir + " " + "steminputs=" + steminputs + " " + "outdir=" + outdir + ' ' + "srcra='16 34 01.61' srcdec='-47 23 34.8' createexpomap=yes useexpomap=yes plotdevice='ps' correctlc=yes cleanup=no &> log"
print('Running pipeline command: ' + xrt)
#os.system(xrt)
#subprocess.Popen(xrt)

