#!/bin/bash
##This script transfers pending jobs from one SLURM partition to another.
##The user can specify how many jobs to transfer.  To transfer all pending jobs, set -n 0.
##Currently, only pending jobs of the logged in user's netid is used.
##Currently, the specific jobs to be transferred are arbitrary picked from the top of the squeue -t PD list.

usage="Usage: switch_part.sh -n [NUMBER_OF_JOBS_TO_TRANSFER] -f [TRANSFER_FROM] -p [TRANSFER_TO]"
##-f is optional.  If omitted, the pending jobs from all partitions will be transferred.

netid=$USER

#Argument processing.
while getopts :n:f:p: option; do
	case $option in
		n)
			numjobs=$OPTARG
			;;
		p)
			transferto=$OPTARG
			;;
		f)
			transferfrom=$OPTARG
			;;
		\?)
			echo "Error: -$OPTARG is not a valid option." >&2
			echo $usage >&2
			exit 1;
			;;
		:)
			echo "Error: -$OPTARG requires an argument." >&2
			echo $usage >&2
			exit 1;
			;;
	esac
done

if [ -o $numjobs ]; then
	echo "The parameter -n (number of jobs) is required." >&2
	exit 1;
fi

if [ -o $transferto ]; then
	echo "The parameter -p (partition to transfer to) is required." >&2
	exit 1;
fi

#Run squeue, depending on whether -f is supplied.  Store in joblist.
if [ ! -o $transferfrom ]; then
	joblist=`squeue -r -u $netid -h -t PD -p $transferfrom -o \%i`
else
	joblist=`squeue -r -u $netid -h -t PD -o \%i`
fi

#Set a flag for the number of jobs transferred.
transferred=0

#Loop over joblist and transfer.
for job in $joblist; do
	#If we have exceeded the number of jobs to be transferred, break out of the for loop.
	#When $numjobs is 0, transfer all pending jobs.
	if [[ $numjobs != 0 ]] && [[ $transferred -ge $numjobs ]] ; then
		break
	fi
	scontrol update jobid=$job partition=$transferto
	
	#Increment the jobs transferred number.
	transferred=$(($transferred+1))
done

#Print a warning if the number of jobs to be transferred is different from the number actually transferred.
if [ $numjobs -eq 0 ]; then
	echo "Transferred all pending jobs ($transferred) to $transferto."
elif [ $transferred -lt $numjobs ]; then
	echo "Warning: Requested that $numjobs get transferred to $transferto, but only transferred $transferred.  There were probably fewer than $numjobs pending."
elif [ $transferred -lt $numjobs ]; then
	echo "Warning: Requested that $numjobs get transferred to $transferto, but transferred $transferred.  Is there an error in the arguments supplied?"
else
	echo "Transferred $numjobs to $transferto."
fi
