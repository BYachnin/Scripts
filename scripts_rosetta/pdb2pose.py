#!/usr/bin/python
## usage: python pdb2pose.py <posefile> <pdb1> <pdb2> <pdb3>.....

import os, sys

from pyrosetta import *
init("-ignore_unrecognized_res")

def main(argv):
    args = sys.argv

    pose = pose_from_pdb(args[1])
    
    for res in range(2,len(args)):
        print("PDB residue " + str(args[res]) + " is Pose residue " + str(pose.pdb_info().pdb2pose(args[res][-1],int(args[res][0:-1]))))

if __name__ == "__main__":
    main(sys.argv[1:])

