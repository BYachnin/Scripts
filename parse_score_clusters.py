#!/usr/bin/python

##Usage: parse_score_clusters.py myscores.csv clusters.txt outscore.csv
##myscores.csv is a list of scores in CSV format.  The pose/filename should be headed "description"
##clusters.txt is the output from BCL:Cluster, and should list all files in the score file.
##outscore.csv is the output file, which will output each node as a block in the CSV file.

import os, sys, csv

scorename = sys.argv[1]
scorefile = open(scorename, 'r')
clustername = sys.argv[2]
clusterfile = open(clustername, 'r')
outname = sys.argv[3]
outfile = open(outname, 'a')

scores = []
nodes = []

#Convert each line of the score file to a list, and put each of those lists into another list.
for line in scorefile:
	line = line.replace('\n','').replace('\r','').replace(' ','').split(',')
	scores.append(line)
	
#Convert each line of the cluster file to a list, and put each of those lists into another list.
for line in clusterfile:
	line = line.replace('\n','').replace(' ','').split(':')
	nodes.append(line)
	
#Go through the header row of the score file and determine what column description is in.
colnum = 0
scorename = -1
for col in scores[0]:
	if (col == 'description'):
		scorename = colnum
	colnum = colnum + 1

#We will assume that the node name is in the first column, the file name is in the third column in the node file, and the leaf is in the 7th column.
nodeid = 0
nodename = 2
nodeleaf = 6

#We are assuming that all of the nodes are written consecutively.
#Loop over the node file.
curnode = ''
for idx,node in enumerate(nodes):
	#Check if the current line is a leaf.
	if ( nodes[idx][nodeleaf] == '0' ): continue
	#Check if the current line is a new node.
	if (curnode != nodes[idx][nodeid]):
		#Set our new current node.
		curnode = nodes[idx][nodeid]
		#Write out the node separator
		outfile.write('--------------'+curnode+'--------------\n')
	#Loop over the score file until we find a leaf for the current PDB file
	found = False
	for scidx,sc in enumerate(scores):
		if ( nodes[idx][nodename] == scores[scidx][scorename] ):
			#Write out that line and break out of the loop.
			#print scores[scidx]
			outfile.write(','.join(map(str,scores[scidx])))
			outfile.write('\n')
			found = True
			break
	if ( found == False ):
		print "The file " + nodes[idx][nodename] + " was not found in the score file."