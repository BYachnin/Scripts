#!/usr/bin/env python

#Usage: pdblist_seq_to_file.py inputlist.txt outputseq.txt
#inputlist.txt is a text file with a list of PDB files, one per line.  .pdb extension is optional.  The PDB files should in the working directory.
#outputseq.txt is the output filename, which will contain the amino acid sequence of all the PDB files, one per line.

import os, sys

infilename = sys.argv[1]
outfilename = sys.argv[2]

infile = open(infilename, 'r')
outfile = open(outfilename, 'w')

filelist = infile.readlines()

from rosetta import *
init("-ignore_unrecognized_res")

for pdb in filelist:
	if ( pdb.endswith(".pdb") or pdb.endswith(".PDB") ):
		pose = pose_from_pdb(pdb.strip())
		outfile.write(pose.sequence()+"\n")
	else:
		pose = pose_from_pdb(pdb.strip() + ".pdb")
		outfile.write(pose.sequence()+"\n")

outfile.close()