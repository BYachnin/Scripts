#!/usr/bin/python
#This script will attempt to execute any slurmit.py-generated sbatch submission script in the current directory.
#It searches for any script named tmp_*.sh and submits it using sbatch.  If successful, the script is deleted.  If not, the script gets terminates.
#Should be used alongside slurmit.py, in cases where slurm prevents submission of all of your jobs.  The failed jobs can be easily re-submitted in this way.

import os, sys, subprocess, glob

#This is an exception class to catch Argument errors.
class ArgError(Exception):
	def __init__(self, msg):
		self.msg = msg
		print(self.msg)
			
def main(argv):	
	#Loop over all slurmit.py scripts in the current directory.  Assuming this is tmp_*.sh.
	for script in glob.glob("tmp_*.sh"):
		#Execute the script.  Keep the error code stored in code_sbatch.
		print(script)
		code_sbatch = subprocess.call(['sbatch', script])
			
		#Clean up the script if code_sbatch is 0, which means that sbatch completed without an error.  Scripts that fail to submit won't be deleted for later re-submission.
		if code_sbatch == 0:
			#Delete the script.
			os.remove(script)
		else:
			break
		
if __name__ == "__main__":
	main(sys.argv[1:])
