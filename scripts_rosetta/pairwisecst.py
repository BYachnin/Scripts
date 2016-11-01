#!/usr/bin/python
## usage: python pairwisecst.py <posefile> <cstfile> <start_res> <end_res> <offset>


import os, sys

from pyrosetta import *
init("-ignore_unrecognized_res")


def main(argv):
    args = sys.argv

    pose_file = args[1]
    cst_file = args[2]
    start_res = int(args[3])
    end_res = int(args[4])
    apply_offset = int(args[5])

    pose = pose_from_pdb(pose_file)

    with open(cst_file, 'w') as afile:
        #afile.write('Resnum Phi Psi Omega\n')   #Some kind of header
        for first_res in range(start_res,end_res):
            atom1 = pose.residue(first_res).xyz("CA")
            for second_res in range(first_res+1,end_res+1):
                atom2 = pose.residue(second_res).xyz("CA")
                diff_vector = atom1 - atom2
                print str(first_res) + " " + str(second_res) + " " + str(diff_vector.norm)
                afile.write('AtomPair CA ' + str(first_res + apply_offset) + ' CA ' + str(second_res + apply_offset) + ' HARMONIC ' + str(diff_vector.norm) + ' 0.2\n')
                #print 'AtomPair CA ' + str(first_res) + ' CA ' + str(second_res) + ' HARMONIC ' + str(diff_vector.norm) + ' 0.2\n'

if __name__ == "__main__":
    main(sys.argv[1:])

