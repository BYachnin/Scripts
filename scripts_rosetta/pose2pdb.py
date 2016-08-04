#!/usr/bin/python
## usage: python pose2pdb.py <posefile> <res1> <res2> <res3>.....

import os, sys

from rosetta import *
init("-ignore_unrecognized_res")

def main(argv):
    args = sys.argv

    pose = pose_from_pdb(args[1])
    
    for res in range(2,len(args)):
        print "Pose residue " + str(args[res]) + " is PDB residue " + str(pose.pdb_info().pose2pdb(int(args[res])))

if __name__ == "__main__":
    main(sys.argv[1:])

