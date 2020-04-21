#!/usr/bin/env python
from pyrosetta import *
init("-ignore_unrecognized_res")

seq_file = open("sequences.fas", "w")

for pdb in sorted(os.listdir(os.getcwd())):
  if pdb.endswith(".pdb") or pdb.endswith(".cif"):
    pose = pose_from_file(pdb)
    seq_file.write(">"+pdb+"\n")
    seq_file.write(pose.sequence()+"\n")
    continue
    
    
    
  else:
    continue
    
seq_file.close()
