#!/usr/bin/python
## usage: python scorepose.py <posefile> <weights>

import os, sys, argparse

from pyrosetta import *
init("-ignore_unrecognized_res")

def main(argv):
    parser = argparse.ArgumentParser(description='My Description')
    parser.add_argument('posefile', type=str)
    parser.add_argument('-w', '--weights', type=str, default='talaris2013')
    parser.add_argument('-s', '--start', type=int)
    parser.add_argument('-e', '--end', type=int)
    args = parser.parse_args()
       
    pose = pose_from_pdb(args.posefile)
    
    myscore = create_score_function(args.weights)
    myscore.show(pose)
    
    if args.start is None:
        print
    else:
        try:
            args.end
        except:
            print "Must define --end if you have defined --start."
        else:
            for res in range(args.start,args.end):
                pose.energies().show(res)

if __name__ == "__main__":
    main(sys.argv[1:])

