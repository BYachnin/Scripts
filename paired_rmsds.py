#This script is meant to be run within PyMOL.
#It will consider a list of PDB files in the current directory.
#For all PDB files, it will calculate the RMSD to all other PDB files over the selection specified in selector.
#The results will be output in a bcl clutster compatible table.

#Set up python and pymol initialization.
from pymol import cmd
import os, sys

#Reinitialize pymol.
pymol.rcinit

selector="decoy and name CA"	#PyMOL selector for the RMSD calculation.

#Intialize variables for the list of pdbfiles and length of longest PDB name.
pdblist = []
longstring = 0

#Iterate over all files in the current directory.
for file in sorted(os.listdir(os.getcwd())):
	#If the file is a PDB file, load it and add it to the list of pdb files.
	#All pdb files will be loaded into the object "decoy", so we have a single multi-state object.
	if file.endswith(".pdb"):
		cmd.load(file, "decoy")
		pdblist.append(file)	
		#If the filename is longer than the longest filename to date, store that new length in longstring.
		if len(file) > longstring: longstring = len(file)

#Intialize variables for the current RMSD list, and a master list containing the full table of RMSDs.
rmslist = []
#Add the top-left corner prefix to the table.
masterlist = [["bcl::storage::Table<double>"]]
#Add the top-row list of PDB files to the master list.
masterlist[0].extend(pdblist)

#Iterate over all PDB files in the pdb file list by index.
for idx in range(0,len(pdblist)):
	#Clear the list of RMSDs.
	rmslist = []
	#Add the current pdb filename to the left column of the row.
	rmslist = [pdblist[idx]]
	#Extend rmslist with the intra-state RMSDs between all states and state idx+1.
	#It is idx+1 because PyMOL starts counting at state 1, and python is indexed at 0.
	#Only atoms in selector are considered.
	rmslist.extend(cmd.intra_rms_cur(selector, idx+1))
	#For the self-self comparison, replace the RMSD value of -1.0 with 0.
	for n,i in enumerate(rmslist):
		if i==-1.0: rmslist[n]=0
	#print rmslist
	#We now have a list containing the name of the PDB file followed by the RMSD to all PDB files.
	#Append this to the masterlist.
	masterlist.append( rmslist )
	
#print masterlist

#Open the rmsds.txt file for output.
rmsd_file = open("rmsds.txt", "a")
#rmsd_file.write(masterlist)

longstring = longstring + 2

#Set up formating strings for the first and subsequent lines in the file.
firstfrmt = '{:'+str(longstring)+'s}' + len(pdblist) * ('{:>'+str(longstring)+'s}')
frmt = '{:'+str(longstring)+'s}' + len(pdblist) * ('{:>'+str(longstring)+'f}')
#print frmt

#Set up flag variable for the first line of the pdb file.
first = True

#Iterate over the outer list in the list-of-lists.  This is the list of lines.
for line in masterlist:
	#If this is the first line, write to the output file using the firstfrmt formatting string.
	if (first):
		#print(firstfrmt.format(*line))
		rmsd_file.write(firstfrmt.format(*line))
		rmsd_file.write('\n')
		first = False
	#If it is a data line, write to the output file using the frmt formatting string.
	else:
		#print(frmt.format(*line))
		rmsd_file.write(frmt.format(*line))
		rmsd_file.write('\n')
		
#We're done.  Close the output file.
rmsd_file.close()
