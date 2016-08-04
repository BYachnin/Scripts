#!/bin/bash

if [ -e pdb_files ]; then
  echo pdb_files directory already exists.  Delete it and re-start the script if you want to continue.  Quitting.
  exit
fi

mkdir pdb_files

for jobdir in */; do
  if [ $jobdir != "pdb_files/" ]; then
    for pdbfile in $jobdir*.pdb; do
#      echo pdb_files/"$pdbfile" | awk -F'/' '{print $NF}'
#      if [[ -e pdb_files/$("$(echo $pdbfile)" | awk -F'/' '{print $NF}') ]]; then
#        echo WARNING: A file named $pdbfile is already present in the pdb_files directory.  Did not copy.
#        echo $pdbfile >> pdb_files/skipped.txt
#      else
        cp $pdbfile pdb_files/
#      fi
    done
  fi
done
