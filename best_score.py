#!/usr/bin/python

##Usage: best_score.py pdblist.txt myscores.sc topnum
##pdblist.txt is a list of PDB names to search for in the score file.
##myscores.sc is a Rosetta scorefile.
##Both files should be in the current directory.
##pdblist.txt must not have the extensions listed.  To do this with ls, use the following command:
##ls | sed -e 's/\..*$//' > pdblist.txt
##topnum is the number of top scores to return.  For example topnum=10 returns the top 10 scores.

import os, sys, csv

pdbfilelist = sys.argv[1]
pdblist = open(pdbfilelist, 'r')
myscores = sys.argv[2]
scorefile = open(myscores, 'r')
topnum = sys.argv[3]

csvscores = []

#Convert each line of the score file to a list, and put each of those lists into another list.
for line in scorefile:
	line = line.split()
	csvscores.append(line)
	
#Go through the header row and determine what column total_score and description are in.
colnum = 0
for col in csvscores[1]:
	if (col == 'total_score'):
		totalcol = colnum
	if (col == 'description'):
		namecol = colnum
	colnum = colnum + 1

bestscores = []

#For each file in the list of PDBs
for posefile in pdblist:
	#Set that we haven't found this pose yet
	foundpose = False
	#Go through each row, keeping track of which number we're on
	rownum = 0
	for row in csvscores:
		#Make sure we are not in a header row
		if ((len(csvscores[rownum]) <= namecol) or (len(csvscores[rownum]) <= totalcol)):
			rownum = rownum + 1
			continue
		#See if that row contains the score for the current PDB file in the list
		if (csvscores[rownum][namecol] == posefile.rstrip()):
			#If so, indicate that we've found the pose
			foundpose = True
			#Add the pose to the list
			bestscores.append((csvscores[rownum][namecol],csvscores[rownum][totalcol]))
			#And since we've found our target, break out of the for loop
			break
		rownum = rownum + 1
	
	if (foundpose == False):
		print "WARNING: The output PDB " + posefile + " given in " + pdbfilelist + " was not found in " + myscores
		
#Sort the list on the totalscore element
bestscores = sorted(bestscores, key=lambda item: item[1])
#Remove the worst scoring poses until we have the desired number left.
while (len(bestscores) > int(topnum)):
	bestscores.pop(0)

#Reverse the list so that we get the answers in order of best to worst energy.
bestscores.reverse()

outfile = open('bestscores.txt', 'a')

print "From the list of output PDBs given in " + myscores + ", the best " + topnum + " scoring poses are:"
for idx in range(len(bestscores)):
	print bestscores[idx][0] + ": " + bestscores[idx][1]
	outfile.write(bestscores[idx][0] + '.pdb\n')

outfile.close()