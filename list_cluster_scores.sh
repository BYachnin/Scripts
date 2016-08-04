#!/bin/bash

for clusterfile in Cluster*.txt; do
	best_score.py $clusterfile ../../score_mg.sc
	done
	
grep '*' 1452821557.fas.1.clstr | sed -e 's/.*>//g' | sed -e 's/.pdb.*//g' >> clustcenters.txt