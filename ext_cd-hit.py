#!/usr/bin/python

##Usage: ext_cd-hit <clusterfile>
##<clusterfile> is the CD-HIT output cluster file.
##It should list clusters starting with >Cluster #, followed by a list (one per line) of all PDB files in the cluster.
##This script will extract each PDB file name (w/o .pdb extension) into a text file for each cluster.

import os, sys, string
from string import whitespace

clusterfilename = sys.argv[1]
clusterfile = open(clusterfilename, 'r')

#Set a variable cur_cluster to be the current cluster.
cur_cluster = ''

#For each line in the cluster file
for line in clusterfile:
	#Check if the current line is the start of a new cluster.  If so, set the new cur_cluster and skip to the next line.
	if (line[0] == '>'):
		#Close any open file.
		try:
			writefile
		except:
			print
		else:
			writefile.close()
			
		#Generate the name of the text file, and then open it as a writeable file.
		cur_cluster = line.translate(None, whitespace).replace('>','') + '.txt'
		writefile = open(cur_cluster, 'w')
		continue
	
	#For each line, take out the PDB filename (excluding .pdb) and write it to the current cluster file.
	writefile.write((line.split('>')[1].split('.pdb')[0]) + '\n')