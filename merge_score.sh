#!/bin/bash

if [ -e score_mg.sc ]; then
  echo Merged score file exists in current directory.  Quitting.
  exit
fi

firstfile=1

for jobdir in */; do
  for scorefile in $jobdir*.sc; do
    if [ -e $scorefile ]; then   
      if [ $firstfile = 1 ]; then
        cat $scorefile > score_mg.sc
        firstfile=0
      else
        tail -n +3 $scorefile >> score_mg.sc
      fi
	fi
  done
done
