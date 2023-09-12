#!/usr/bin/python3

# NAME:
#	swift.py
#
# PURPOSE:
#	To automate the processing (post level 1) of the observational data collected from the Swift XRT
#
# EXPLANATION:
#		 
#
# CALLING SEQUENCE:
#
#
# OUTPUTS:
#
#
# EXAMPLES:
#
#
# AUTHORS:
#        K.Zaidi           May, 2018

import subprocess, os, re, time

inputTxt = "swift.txt"

script_path = os.path.abspath(__file__)

index = script_path[::-1].find("/")
parentDir = script_path[::-1][index+1:]
parentDir = parentDir[::-1]
##################################################################     PC/WT     ########################################################################################

#reads lines of the input.txt file into a list
inputFile = open(parentDir +"/"+ inputTxt,'r')               #open the swift file    
lineNum = 0                                     #initialize the line count
obsdir = []                                 	#initializing the array to hold the location of the observation directories given by swift

for line in inputFile.readlines():              #loop to record the information from the file in 'attributes'
	line = line.strip('\n\r')
	obsdir.append(line)
	lineNum += 1
inputFile.close()

for eachObs in obsdir:
	ev = '/xrt/event'
	obsdir = eachObs
	evtdir = obsdir + ev

	#creating obsdir_reduced for outdir
	obsdir_temp = obsdir[::-1]
	obsdir_reduced = obsdir_temp[obsdir_temp.find('/'):]
	obsdir_reduced = obsdir_reduced[::-1]

	#creating obsid from obsdir
	obsid_temp = obsdir_temp[:obsdir_temp.find('/')]
	#print(obsid_temp)
	obsid = obsid_temp[::-1]
	print(obsdir)
	#determines if an observation was recorded in a PC or a WT mode
	if (os.path.exists(obsdir)):            
		event = os.listdir(evtdir)     		#array holds the foldernames in the observation directory
		try:
			mode = event[2]                         #mode holds the appropriate foldername in the observation directory to look for observation mode used
		except:
			mode = event[0]
			
		PC = re.search('pc',mode, re.M|re.I)    #uses re to search for the 'pc' or 'wt' in the appropriate foldername to decide the mode of the observation
		WT = re.search('wt',mode, re.M|re.I)
		if PC:
			print('Current observation mode: PC')
			obmode = 'pc'
		elif WT:
			print('Current observation mode: WT')
			obmode = 'wt'
	else:
		print('Observation not found')

	####################################################################     XRTPIPELINE     ################################################################################

	#recording ObsID
	#obsid = evtdir_split[4] 
	print('ObsID: ' + obsid)

	#Input directory for running xrtpipeline
	indir = obsdir
	print('indir:' + indir)

	#steminputs for xrtpipeline
	steminputs = 'sw' + obsid
	print('steminputs: ' + steminputs)

	#output directory for screened files coming out of xrtpipeline
	outdir = obsdir_reduced  + obsid + '-xrt'
	print('outdir: ' + outdir)
	
	#name of the file where the log of xrtpipeline is recorded
	xrtlog = 'xrt_' + obsid + '.log'

	xrt = 'xrtpipeline indir=' + indir + ' steminputs=' + steminputs + ' outdir=' + outdir + ' srcra=' + 'OBJECT' + ' srcdec=' + 'OBJECT' + ' createexpomap=yes useexpomap=yes plotdevice="ps" correctlc=yes  clobber=yes cleanup=no > ' + xrtlog
	print('Running pipeline command: ' + xrt)


	os.system(xrt)

	#######################################################################     XSELECT      ################################################################################

	#changing to outdir directory for xselect work
	os.chdir(outdir)

	#(NOT A PART OF XSELECT) finding the rmf file in CALDB and copying it to the outdir
	p = subprocess.Popen( "quzcif SWIFT XRT - - matrix - - datamode.eq.windowed.and.grade.eq.G0:2.and.XRTVSUB.eq.6", stdout=subprocess.PIPE, shell=True)
	(quzcif_output, err) = p.communicate()
	p_status = p.wait()

	quzcif = str(quzcif_output)
	quzcif = quzcif.strip("1b\\n' ").split(" ")
	quzcifFile = quzcif[-1].strip("1b\\n'")
	os.system('cp '+  quzcifFile + ' ' + outdir)
	#time.sleep(15)
	print('rmf file location: ' + quzcifFile)


	#recording the filenames of the event directory in an array to be searched in below
	xrt_filelist = os.listdir(outdir)

	#finding the appropriate event file
	for evt in xrt_filelist:
		if "po_cl.evt" in evt:
			xrt_evtfile = evt
			break

	#finding the region file in the screened xrt files
	for reg in xrt_filelist:
		if ("reg" in reg) and ("po" in reg):
			regfile = reg
			break

	#reading the source coordinates from the region file created by the xrtpipeline
	regfile_cood = open(regfile, 'r')
	cood = regfile_cood.read()
	regfile_cood.close()
	cood = cood[cood.find('(')+1 : cood.find(')')]
	cood = cood.split(',')
	srcx = cood[0]
	srcx = float(srcx)
	srcy = cood[1]
	srcy = float(srcy)

	# Region manipulation for PC
	if obmode == 'pc':
		srcxr = srcx + 100
		srcxl = srcx - 100
		srcyu = srcy + 100
		srcyd = srcy - 100
		backr = 'sw' + obsid + 'back_right.reg'
		back_right = open(backr, 'w')
		back_right.write('CIRCLE (' + str(srcxr) + ',' + str(srcy) + ',20)')
		back_right.close()
		backl = 'sw' + obsid + 'back_left.reg'
		back_left = open(backl, 'w')
		back_left.write('CIRCLE (' + str(srcxl) + ',' + str(srcy) + ',20)')
		back_left.close()
		backu = 'sw' + obsid + 'back_up.reg'
		back_up = open(backu, 'w')
		back_up.write('CIRCLE (' + str(srcx) + ',' + str(srcyu) + ',20)')
		back_up.close()
		backd = 'sw' + obsid + 'back_down.reg'
		back_down = open(backd, 'w')
		back_down.write('CIRCLE (' + str(srcx) + ',' + str(srcyd) + ',20)')
		back_down.close()
		xsel_PC = 'xsel' + obsid + '_PCback.xco'
		xsel_pcback = open(xsel_PC, 'w')
		xsel_pcback.write('xsel' + obsid + '\nno\n')
		xsel_pcback.write('read e'+ '\n')
		xsel_pcback.write(outdir + '\n')
		xsel_pcback.write(xrt_evtfile + '\n' + 'yes' + '\n')
		xsel_pcback.write('filter region ' + backr + '\nextract spectrum\nyes\n')
		xsel_pcback.write('clear region\nfilter region ' + backl + '\nextract spectrum\nyes\n')
		xsel_pcback.write('clear region\nfilter region ' + backu + '\nextract spectrum\nyes\n')
		xsel_pcback.write('clear region\nfilter region ' + backd + '\nextract spectrum\nyes\n')
		xsel_pcback.write('$cd\n')
		xsel_pcback.write('no\nquit\nyes')
		xsel_pcback.close()
		os.system('xselect @' + xsel_PC)
		back_xpec = []
		counts = []
		back_pcreg = open('xselect.log','r')
		for line in back_pcreg.readlines():
			if (re.search('Spectrum         has', line, re.M|re.I)):
				back_xpec.append(line)
		back_pcreg.close()
		for item in back_xpec:
			item = item[25:item.find('coun')]
			item = str(item).strip()
		item = int(item)
		counts.append(item)
		min_ = min(counts)
		pc_backindex = counts.index(min_)
	# Region manipulation for WT
	elif obmode == 'wt':
		back = 'sw' + obsid + 'back.reg'
		backfile = open(back, 'w')
		backfile.write('annulus (' + str(srcx) + ',' + str(srcy) + ',90,110)\n')
		backfile.close()

	#Writing the .xco file for XSELECT to read the commands from
	print('Event file directory:' + outdir)	#see outdir above

	xsel_filename = 'xsel' + obsid + '.xco'
	xsel_file = open(xsel_filename, 'w')
	xsel_file.write('xsel' + obsid + '\nno\n')
	xsel_file.write('read e'+ '\n')
	xsel_file.write(outdir + '\n')

	#adding further things to the .xco file
	xsel_file.write(xrt_evtfile + '\n' + 'yes' + '\n')
	xsel_file.write('filter region ' + regfile + '\nextract spectrum\nsave spectrum sw' + obsid + '_spectrum.pha\nyes\nclear region\n')
	if obmode == 'pc':
		if pc_backindex == 0:
			xsel_file.write('filter region ' + backr + '\nextract spectrum\nsave spectrum sw' + obsid + 'back_spectrum.pha\nyes\n')
		elif pc_backindex == 1:	
			xsel_file.write('clear region\nfilter region ' + backl + '\nextract spectrum\nsave spectrum sw' + obsid + 'back_spectrum.pha\nyes\n')
		elif pc_backindex == 2:	
			xsel_file.write('clear region\nfilter region ' + backu + '\nextract spectrum\nsave spectrum sw' + obsid + 'back_spectrum.pha\nyes\n')
		elif pc_backindex == 3:
			xsel_file.write('clear region\nfilter region ' + backd + '\nextract spectrum\nsave spectrum sw' + obsid + 'back_spectrum.pha\nyes\n')
	elif obmode == 'wt':
		xsel_file.write('filter region ' + back + '\nextract spectrum\nsave spectrum sw' + obsid + 'back_spectrum.pha\nyes\n')
	#xsel_file.write('$cd\n')
	xsel_file.write('no\nquit\nno')
	xsel_file.close()

	os.system('xselect @' + xsel_filename)

	#changing back to starting working directory
	#os.chdir(wd)

	#finding the arf file in the screened xrt files
	for arf in xrt_filelist:
		if (re.search('arf', arf, re.M|re.I)):
			if (re.search('po', arf, re.M|re.I)):
				arffile = arf
	print('arf file: ' + arffile)

	#finding the rmf file in the xrt files (was copied here from CALDB)
	for rmf in xrt_filelist:
		if (re.search('rmf', rmf, re.M|re.I)):
			rmffile = rmf
	print('rmf file: ' + rmffile)


	#grppha
	grp_out = '!sw' + obsid + '_grp.pha'
	backfile = 'sw' + obsid + 'back_spectrum.pha'
	grppha = "grppha infile= '" + "sw" + obsid + "_spectrum.pha'" + " outfile='" + grp_out + "' chatter=0 comm='group min 10 & bad 0-29 & chkey backfile " + backfile + " chkey ancrfile " + arffile + " & chkey respfile " + rmffile + " & exit'"
	print(grppha)
	os.system(grppha)

#########################################################################################################################################################################
