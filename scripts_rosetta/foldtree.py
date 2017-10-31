#!/usr/bin/python
## usage: python pose2pdb.py <posefile>

import os, sys

from pyrosetta import *
init("-ignore_unrecognized_res")

def main(argv):
    args = sys.argv

    pose = pose_from_pdb(args[1])
    
    print "The foldtree for pose " + args[1] + " is:\n"
    print pose.fold_tree()

if __name__ == "__main__":
    main(sys.argv[1:])

