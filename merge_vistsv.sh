#!/bin/bash

if [ -e score_mg.tsv ]; then
  echo Merged score file exists in current directory.  Quitting.
  exit
fi

firstfile=1

for jobdir in */; do
  for scorefile in ${jobdir}*_scores.tsv; do
    if [ -e $scorefile ]; then   
      if [ $firstfile = 1 ]; then
        cat $scorefile > score_mg.tsv
        firstfile=0
      else
        tail -n +2 $scorefile >> score_mg.tsv
      fi
	fi
  done
done
