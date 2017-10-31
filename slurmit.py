#!/usr/bin/python

import os, sys, argparse, subprocess

#This is an exception class to catch Argument errors.
class ArgError(Exception):
	def __init__(self, expr, msg):
		self.expr = expr
		self.msg = msg
		
#This function returns a list of tuples.  Each item in the list corresponds to one argument taken from the command line.
#The members of the tuple describe how the variable should be handled in various places.
#To change the behaviour of an argument or to add new variables, add or modify the tuples here.
def gen_varkey():
	vars = []
	
	#(0 arg.varname, 1 SLURM variable name, 2 variable type, 3 default, 4 required, 5 class)
	vars.append(('job', 'job-name', str, None, True, 'regular'))
	vars.append(('partition', 'partition', str, 'main', False, 'regular'))
	vars.append(('requeue', 'requeue', bool, True, False, 'boolean'))
	vars.append(('tasks', 'ntasks', int, 1, False, 'regular'))
	vars.append(('cpus', 'cpus-per-task', int, 1, False, 'regular'))
	vars.append(('mem', 'mem', str, "2000", False, 'regular'))
	vars.append(('outfiles', None, str, "", False, 'other'))
	vars.append(('log', 'output', str, "", False, 'regular'))
	vars.append(('err', 'error', str, "", False, 'regular'))
	vars.append(('time', 'time', str, "3-00:00:00", False, 'regular'))
	vars.append(('execute', None, bool, True, False, 'other'))
	vars.append(('cleanup', None, bool, True, False, 'other'))
	vars.append(('command', None, str, None, True, 'other'))
	#--export=ALL
	
	return vars

def gen_argparser(argv, key):
	#Parse command line arguments (argv) using the information stored in the list of tuples.
	parser = argparse.ArgumentParser(description='My Description')
	#parser.add_argument('--job-name', type=str, required=True)
	#parser.add_argument('--partition', type=str, default='main')
	#parser.add_argument('--requeue', type=bool, default=True)
	#parser.add_argument('--ntasks', type=int, default=1)
	#parser.add_argument('--cpus-per-task', type=int, default=1)
	#parser.add_argument('--mem', type=str, default="2000")
	#parser.add_argument('--outfiles', type=str, default="")
	#parser.add_argument('--output', type=str, default="")
	#parser.add_argument('--error', type=str, default="")
	#parser.add_argument('--time', type=str, default="3-00:00:00")
	#parser.add_argument('--execute', type=bool, default=True)
	#parser.add_argument('--cleanup', type=bool, default=True)
	#parser.add_argument('--command', type=str, required=True)
	for argnum in range(0, len(key)):
		parser.add_argument('--'+key[argnum][0], type=key[argnum][2], default=key[argnum][3], required=key[argnum][4])
	
	#--export=ALL
	args = parser.parse_args()
	return(args)
	
#This function should examine the input and determine if there are any problems.
#Hopefully return a helpful error message and quit if a problem is detected.
def validate(args):
	#If the user specifies --outfiles (identical prefixes for the log and the error files), they cannot specifiy either --output or --error.
	try:
		if args.outfiles != '' and (args.log != '' or args.err != ''):
			raise ArgError('You have provided both a value for both --outfiles and --log and/or --err.  If you provide --outfiles, you cannot provide --log or --err.')
	except ArgError:
		exit()
		
	#--mem is input as a string, as it can be listed as an integer in MB (eg. --mem 10000) or a value with a suffix (eg. --mem 10G).
	#Check to what is input is valid.
	try:
		if args.mem[-1] in ['K', 'M', 'G', 'T']:
			int(args.mem[:-1])
		else:
			int(args.mem)
	except ValueError:
		exit("--mem must be provided as an integer or an integer followed by the suffix K, M, G, or T for kilobyte, megabyte, gigabyte, or terrabyte.")

#Make final variable values depending on the user input.
def arg_logic(args, key):
	#If outfiles, outfiles, log, and err are all empty, generate log and err based on jobname.
	if (args.outfiles == '' and args.log == '' and args.err == ''):
		args.log = args.job + '.out'
		args.err = args.job + '.err'
		
	#If outfiles is defined, set log and err based on outfiles.
	if (args.outfiles != ''):
		args.log = args.outfiles + '.out'
		args.err = args.outfiles + '.err'
		
	return(args)
		
#This function creates and returns the SLURM script as a list, where each list item is a line in the file.
#It uses the command line arguments (args) and the list of tuples to figure out what to do with it all.
def make_script(args, key):
	#Add the #! and --export=ALL.
	script = ['#!/bin/bash', '#SBATCH --export=ALL\n']
	
	#argnum = 0
	#for argnum in range(0, len(args)):
	
	#Loop over all arguments in the key.
	for argnum in range(len(key)):
		#Do not add a line unless we have processed this variable and switched the flag on addline.
		addline = False
		#If this is a "regular" variable that takes an argument, process it this way.
		if key[argnum][5] == 'regular':
			line = "#SBATCH --" + key[argnum][1] + " " + str(getattr(args, key[argnum][0])) + "\n"
			addline = True
		#If this is a "boolean" variable that shows up or not in the SLURM script, but doesn't take an argment, process this way.
		if key[argnum][5] == 'boolean':
			if getattr(args, key[argnum][0]) == True:
				line = "#SBATCH --" + key[argnum][1] + "\n"
				addline = True
		
		#If we processed the line for this variable, add it to the script list of lines.
		if addline == True:
			script.append(line)
		#argnum = argnum + 1
		
	# for boolarg in [arg.requeue]:
		# if boolarg == True:
			# line = "#SBATCH --requeue\n"
		# script.append(line)
		
	#Add the command line to the bottom of the script.
	script.append(args.command)
	
	return(script)
			
#Write all the data in script to the file scriptname.
def write_script(script, scriptname):
	outfile = open(scriptname, 'w')
	for line in script:
		outfile.write(line)
	outfile.close()
			
def main(argv):
	#Setup a list of tuples.  Each tuple should contain:
	#(0 arg.varname, 1 SLURM variable name, 2 variable type, 3 default, 4 required, 5 class)
	#class should be 'regular' for SLURM parameters that receive an argument, 'boolean' for those that either appear or do not, and
	#'other' for other types of arguments.
	varkey = gen_varkey()

	#Generate the argument list using argparser
	args = gen_argparser(argv, varkey)
	
	#Validate arguments
	validate(args)
	
	#Generate "logical defaults" based on the input arguments.
	procargs = arg_logic(args, varkey)
	
	#Process the arguments and generate the slurm script.
	slurm_script = make_script(procargs, varkey)
	
	for line in slurm_script:
		print(line)
	
	#Make a filename from the jobname, and then write the script.
	scriptname = 'tmp_' + args.job + '.sh'
	write_script(script, scriptname)
	
	#If desired, execute the script.
	if args.execute == True:
		#Run the script, waiting for it to finish.
		subprocess.call('sbatch ' + scriptname)
		
	#If desired, cleanup the script.
	if args.cleanup == True:
		#Delete the script.
		os.remove(scriptname)
		
if __name__ == "__main__":
	main(sys.argv[1:])

