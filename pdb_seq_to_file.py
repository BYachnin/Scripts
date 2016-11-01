#!/usr/bin/env python
from pyrosetta import *
init("-ignore_unrecognized_res")

seq_file = open("sequences.txt", "w")

for pdb in sorted(os.listdir(os.getcwd())):
  if pdb.endswith(".pdb"):
    pose = pose_from_pdb(pdb)
    seq_file.write(pose.sequence()+"\n")
    continue
    
    
    
  else:
    continue
    
seq_file.close()