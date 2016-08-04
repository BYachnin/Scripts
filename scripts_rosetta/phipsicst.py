#!/usr/bin/python
## usage: python phipsicst.py <posefile> <cstfile> <start_res> <end_res> <offset>


import os, sys

from rosetta import *
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
        for res in range(start_res,end_res+1):
            phi = pose.phi(res)
            psi = pose.psi(res)
            print "Phi angle for " + str(res) + ": " + str(phi)
            afile.write('Dihedral C ' + str(res - 1 + apply_offset) + ' N ' + str(res + apply_offset) + ' CA ' + str(res + apply_offset) + ' C ' + str(res + apply_offset) + ' HARMONIC ' + str(phi) + ' 20\n')
            print "Psi angle for " + str(res) + ": " + str(psi)
            afile.write('Dihedral N ' + str(res + apply_offset) + ' CA ' + str(res + apply_offset) + ' C ' + str(res + apply_offset) + ' N ' + str(res + 1 + apply_offset) + ' HARMONIC ' + str(psi) + ' 20\n')

if __name__ == "__main__":
    main(sys.argv[1:])

