#!/usr/bin/python3
import subprocess, os, re


##################################################################     PC/WT     ########################################################################################

#reads lines of the input .txt file into a list
inputFile = open('swift.txt','r')               #open the swift file    
lineNum = 0                                     #initialize the line count
obsdir = []                                 #initializing the array to hold the location of the observation directories given by swift

for line in inputFile.readlines():              #loop to record the information from the file in 'attributes'
        line = line.strip('\n\r')
        obsdir.append(line)
        lineNum += 1
inputFile.close()
ev = '/xrt/event'
evtdir = obsdir[0] + ev
#print(obsdir)
print(evtdir)

#determines if an observation was recorded in a PC or a WT mode
if (os.path.exists(obsdir[0])):             #the zeroth element of attributes is the first line of swift.txt
        event = os.listdir(evtdir)     		#array holds the foldernames in the observation directory
        mode = event[2]                         #mode holds the appropriate foldername in the observation directory to look for observation mode used
        PC = re.search('pc',mode, re.M|re.I)    #uses re to search for the 'pc' or 'wt' in the appropriate foldername to decide the mode of the observation
        WT = re.search('wt',mode, re.M|re.I)
        if PC:
                print('Current observation mode: PC')
        elif WT:
                print('Current observation mode: WT')
else:
        print('Observation not found')


####################################################################     XRTPIPELINE     ################################################################################



line2 = evtdir				#line2 is the second line in the .txt input file which contains the directory for the event file
line2 = line2.split('/')
#print(line2)
line2.reverse()
#print(line2)

#recording ObsID
obsid = line2[2] 
print('ObsID: ' + obsid)

#Input directory for running xrtpipeline
indir = './' + line2[3] + '/' + obsid 		#3 and 4 correspond to the 3rd and 4th elements separated by '/' in swift.txt line 1
print('indir:' + indir)

#steminputs for xrtpipeline
steminputs = 'sw' + obsid
print('steminputs: ' + steminputs)

#output directory for screened files coming out of xrtpipeline
outdir = './' + obsid + '-xrt'
print('outdir: ' + outdir)

xrt = 'xrtpipeline indir=' + indir + ' steminputs=' + steminputs + ' outdir=' + outdir + ' srcra=' + 'OBJECT' + ' srcdec=' + 'OBJECT' + ' createexpomap=yes useexpomap=yes plotdevice="ps" correctlc=yes clobber=yes cleanup=no > xrt.log'
print('Running pipeline command: ' + xrt)


os.system(xrt)
#os.system('$xselect')
#subprocess.Popen(xrt)


#######################################################################     XSELECT      ################################################################################


#Writing the .xco file for XSELECT to read the commands from
print('Event file directory:' + outdir)	#see outdir above
xsel_filename = 'xsel' + obsid + '.xco'
xsel_file = open(xsel_filename, 'w')
xsel_file.write('xsel' + obsid + '\n')
xsel_file.write('read e'+ '\n')
xsel_file.write(outdir + '\n')

#recording the filenames of the event directory in an array to be searched in below
xrt_filelist = os.listdir(outdir)

#finding the appropriate event file
for evt in xrt_filelist:
	if (re.search('cl', evt, re.M|re.I)):
		if (re.search('po', evt, re.M|re.I)):
			if (re.search('.evt', evt, re.M|re.I)):
				xrt_evtfile = evt

#finding the region file in the screened xrt files
for reg in xrt_filelist:
	if (re.search('reg', reg, re.M|re.I)):
		if (re.search('po', reg, re.M|re.I)):
			regfile = reg

#adding further things to the .xco file
xsel_file.write(xrt_evtfile + '\n' + 'yes' + '\n' + 'extract all' + '\n')
xsel_file.write('$cd ' + outdir + '\n')
xsel_file.write('filter region ' + regfile + '\nextract spectrum\nsave spectrum sw' + obsid + '_spectrum.pi\n')
#xsel_file.write('filter region backreg.reg\n')
xsel_file.write('$cd\n')
xsel_file.write('no\nquit\nno')

xsel_file.close()
os.system('xselect @' + xsel_filename)

#finding the arf file in the screened xrt files
for arf in xrt_filelist:
        if (re.search('arf', arf, re.M|re.I)):
                if (re.search('po', arf, re.M|re.I)):
                        arffile = arf
print('arf file: ' + arffile)

#finding the rmf file in CALDB and copying it to the outdir
p = subprocess.Popen( "quzcif SWIFT XRT - - matrix NOW - datamode.eq.windowed.and.grade.eq.G0:2.and.XRTVSUB.eq.6", stdout=subprocess.PIPE, shell=True)
(quzcif_output, err) = p.communicate()
#p_status = p.wait()
quzcif = str(quzcif_output)
quzcif = quzcif.strip("b' 1\n")
quzcif = quzcif[:-3]
quzcif = quzcif.strip()
os.system('cp '+  quzcif + ' ' + outdir)
print('rmf file location: ' + quzcif + '\nrmf file copied successfully to: ' + outdir)

#finding the rmf file in the xrt files (was copied here from CALDB)
for rmf in xrt_filelist:
	if (re.search('rmf', rmf, re.M|re.I)):
		rmffile = rmf
print('rmf file: ' + rmffile)


#grppha
grppha = 'grppha infile= "' + 'sw' + obsid + '_spectrum.pi"' + ' outfile="' + 'sw2.pi"' + ' chatter=0 comm="group min 10 & bad 0-29 & chkey ancrfile ' + arffile + ' & chkey respfile ' + rmffile + ' & exit"'
print(grppha)
os.system(grppha)

#region = open('backreg.reg', 'w')
#region.write('CIRCLE (423.05214301257,496.450702630832,20)')
#region.close()
#########################################################################################################################################################################
