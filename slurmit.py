#!/usr/bin/python

from typing import List

import argparse
import glob
import os
import subprocess
import sys

# This is an exception class to catch Argument errors.
class ArgError(Exception):
    def __init__(self, msg):
        self.msg = msg
        print(self.msg)


class SlurmArgument:
    """
    This is a class that holds data on a SLURM argument that can be extracted from an ArgParse context
    """

    def __init__(self, slurm_var: str, cmdvar: str, vartype: type, default=None, always_include: bool = True):
        """
        Initialization of SlurmArgument

        :param slurm_var: The name of the SLURM variable.  For example,
        :param cmdvar: The name of the argparser variable name containing this value
        :param vartype: [description]
        :param default: The default value for this SLURM variable, defaults to None
        :param required: Include this variable in the script even if it's not passed in, defaults to False
        :return: [description]
        """

        self.slurm_var = slurm_var
        self.cmdvar = cmdvar
        self.vartype = vartype
        self.default = default
        self.always_include = always_include


    def generate_slurmtxt(self, value) -> str:
        """
        Generate the string for a SLURM variable line

        :param value: The value to assign to the SLURM variable
        :return: Text for a SLURM script line
        """

        if self.always_include or (value != self.default):
            line = "#SBATCH --" + self.slurm_var + " " + value + "\n"

        return line


class SlurmBuilder:
    """
    Class to manage argument parser and SlurmArguments
    """

    def __init__(self):
        """
        """

        # Generate an argument parser object for the class.
        self.parser = argparse.ArgumentParser(description='This script generates a SLURM script for a desired command.'
                                              '  You must provide the job name and the command.  SLURM options can be '
                                              'changed to alter your typical #SBATCH variables.  The options below '
                                              'list the SLURM options being controlled in parentheses.')
        self.array_group = self.parser.add_argument_group("array", "Arguments related to array jobs.")

        # Initialize a list that will contain SlurmArguments
        self.slurmargs = []


    def add_control_arg(self, cmd_var: str, vartype: type, default=None, choices: List = None, action: str = "store",
                        helptxt: str = "", array_var: bool = False):
        """
        Add an execution control (i.e. not SLURM) argument to self.parser

        :param cmd_var: command-line argument name
        :param vartype: argparse data type that will be passed to this variable
        :param default: The default value in the
        :param choices: A list of choices allowed for this argument
        :param action: [description], defaults to "store"
        :param always_include: [description], defaults to True
        :param helptxt: [description], defaults to ""
        :param array_var: Argument will be passed to the array group instead of the main parser
        """

        # Add the argument to the argparser
        if array_var:
            self.array_group.add_argument("--" + cmd_var, help=helptxt, type=vartype, action=action, default=default,
                                          choices=choices)
        else:
            self.parser.add_argument("--" + cmd_var, help=helptxt, type=vartype, action=action, default=default,
                                     choices=choices)


    def add_slurm_arg(self, cmd_var: str, vartype: type, slurm_var: str = None, default=None,
                      choices: List = None, action: str = "store", always_include: bool = True, helptxt: str = "",
                      array_var: bool = False):
        """
        Add a slurm-type argument to self.parser and self.slurmargs

        :param cmd_var: command-line argument name
        :param vartype: argparse data type that will be passed to this variable
        :param slurm_var: The SLURM variable name
        :param default: The default value for argparse
        :param choices: A list of choices allowed for this argument
        :param action: argparser action for this variable, like "store_true"
        :param always_include: If True, this will be added to the sbatch script regardless of whether a value is passed.  If False, it will only be included if a non-default value is passed in.
        :param helptxt: The argparse help text.
        :param array_var: Argument will be passed to the array group instead of the main parser
        """

        # Set slurm_var to cmd_var if it's not given.
        if slurm_var is None:
            slurm_var = cmd_var

        # Check that choices are of the right type
        if choices is not None:
            if not all([isinstance(choice, vartype) for choice in choices]):
                raise ArgError("Not all choices for --{cmd_var} are of type {vartype}".format(cmd_var=cmd_var,
                                                                                              vartype=vartype))

        # Add the argument to the argparser
        self.add_control_arg(cmd_var=cmd_var, vartype=vartype, helptxt=helptxt, action=action, default=default,
                             choices=choices, array_var=array_var)

        # Create a SlurmArgument
        slurm_arg = SlurmArgument(slurm_var=slurm_var, cmdvar=cmd_var, vartype=vartype, default=default,
                                  always_include=always_include)

        # Add the slurm_arg to the list
        self.slurmargs.append(slurm_arg)


    @staticmethod
    def validate(args):
        """
        This function validates the results of parsing self.parser's arguments.

        :param args: The result of self.parser.parse_args()
        """

        # If the user specifies --outfiles (identical prefixes for the log and the error files), they cannot specifiy either --output or --error.
        if args.outfiles is not None and (args.log is not None or args.err is not None):
            raise ArgError('You have provided both a value for both --outfiles and --log and/or --err.  If you provide '
                           '--outfiles, you cannot provide --log or --err.')

        # --mem is input as a string, as it can be listed as an integer in MB (eg. --mem 10000) or a value with a suffix (eg. --mem 10G).
        # Check to see if input is valid.
        if args.mem[-1] in ['K', 'M', 'G', 'T']:
            try:
                int(args.mem[:-1])
            except ValueError:
                raise ArgError("--mem must be provided as an integer or an integer followed by the suffix K, M, G, or "
                               "T for kilobyte, megabyte, gigabyte, or terrabyte.")
        else:
            try:
                int(args.mem)
            except ValueError:
                raise ArgError("--mem must be provided as an integer or an integer followed by the suffix K, M, G, or "
                               "T for kilobyte, megabyte, gigabyte, or terrabyte.")

        # If using arrays, make sure %a is in output and error filenames, and '$job' is in the command script.
        if args.array is not None or args.arraygen is not None:
            # Check for %a in the logs.
            if args.outfiles is not None and '%a' not in args.outfiles:
                raise ArgError('You have created an array submission without putting %a in the --outfiles parameter.')
            if args.log is not None and '%a' not in args.log:
                raise ArgError('You have created an array submission without putting %a in the --log parameter.')
            if args.err is not None and '%a' not in args.err:
                raise ArgError('You have created an array submission without putting %a in the --err parameter.')

            # If we are using numeric arrays only, make sure $job is in --command.
            if args.arraygen is None and "$job" not in args.command:
                raise ArgError("You have created a numeric array submission (ie. without --arraygen) without putting "
                               "'$job' in the --command parameter.")

            # If we are using file-based arrays, make sure $file is in --command.
            if args.arraygen is not None and "$file" not in args.command:
                raise ArgError("You have created an array submission with --arraygen without putting '$file' in the "
                               "--command parameter.")

            # If we are using special filename arrays, make sure arrayformat contains arr and [$job].
            if args.arrayformat is not None and '$arr' not in args.arrayformat:
                raise ArgError("You have given --arrayformat without referencing $arr.  The $arr variable is used to "
                               "access the array elements, and must be included in --arrayformat.")
            if args.arrayformat is not None and "[$job]" not in args.arrayformat:
                raise ArgError("You have given --arrayformat without referencing $job.  You must include $job for "
                               "substitution of the array index.")
        # If we aren't using arrays, make sure arrayformat and sleep are None
        else:
            if args.arrayformat is not None:
                raise ArgError("You have given --arrayformat, but aren't using --arraygen.")
            if args.sleep is not None:
                raise ArgError("You have given --sleep, but aren't using --array or --arraygen.")


    @staticmethod
    def process(args) -> argparse.Namespace:
        """
        Based on values passed in to the argparser, reset SLURM values as necessary and return them.

        :param args: The result of self.parser.parse_args()
        :return: The processed args.
        """

        # If outfiles, outfiles, log, and err are all empty, generate log and err based on jobname.
        if args.outfiles is None and args.log is None and args.err is None:
            args.log = args.job + '.log'
            args.err = args.job + '.err'

        # If outfiles is defined, set log and err based on outfiles.
        if args.outfiles is not None:
            args.log = args.outfiles + '.log'
            args.err = args.outfiles + '.err'

        # If args.array is empty and args.arraygen is provided, figure out args.array based on the number of
        # args.arraygen files.
        if args.array is None and args.arraygen is not None:
            # Glob args.usearray
            filelist = glob.glob(args.arraygen)
            arraylen = len(filelist)
            args.array = "0-" + str(arraylen - 1)

        # If args.openmode is not defined, set it according to whether requeue is set.
        # If it is defined, use whatever the user said.
        if args.openmode is None:
            if args.norequeue:
                args.openmode = 'truncate'
            else:
                args.openmode = 'append'

        return(args)


    def parse_args(self) -> argparse.Namespace:
        """
        Parse the args from self.parser and return the args Namespace object.  Includes validation and processing steps.
        """

        args = self.parser.parse_args()

        self.validate(args)
        args = self.process(args)

        return args


    def write_slurm_script(self, args):
        """
        Process the args through the list of SlurmArguments to get a SLURM submission script.

        :param args: An argparse object
        """

        # Write the first two lines of the script
        script = script = ['#!/bin/bash\n', '#SBATCH --export=ALL\n']

        # Loop over self.slurmargs and add each one in turn to the script
        for s_arg in self.slurmargs:
            arg_value = args.__dict__[s_arg.cmdvar]
            script.append(s_arg.generate_slurmtxt(arg_value))



def build_slurm() -> SlurmBuilder:
    """
    This function creates a SlurmBuilder with relevant argparse arguments set up.

    :return: A completely initiazed SlurmBuilder with arguments.
    """

    slurm_builder = SlurmBuilder()
    slurm_builder.add_slurm_arg(cmd_var="job", vartype=str, slurm_var="job-name", helptxt="The "
                                "SLURM name for your job (--job-name).  Will be used to generate log/err filenames if "
                                "not given, in which case it will genereate the files in the current directory.")
    slurm_builder.add_slurm_arg(cmd_var="partition", vartype=str, default="main", helptxt="The "
                                "SLURM partition to run on (--partition).")
    slurm_builder.add_slurm_arg(cmd_var="no_requeue", vartype=bool, slurm_var="requeue", action="store_true",
                                helptxt="Turn off SLURM's requeue option (on by default).")
    slurm_builder.add_slurm_arg(cmd_var="openmode", vartype=str, slurm_var="open-mode", choices=["truncate", "append"],
                                helptxt="Should the log and err files be overwritten (truncate) "
                                "or appended (append) if the file already exists.  The default is truncate, unless "
                                "requeue is set, in which case the default append.")
    slurm_builder.add_slurm_arg(cmd_var="tasks", vartype=int, slurm_var="ntasks", default=1, helptxt="The number of "
                                "SLURM tasks to request (--ntasks).")
    slurm_builder.add_slurm_arg(cmd_var="cpus", vartype=int, slurm_var="cpus-per-task", default=1, helptxt="The number "
                                "of CPUs to request for each task (--cpus-per-task).")
    slurm_builder.add_slurm_arg(cmd_var="mem", vartype=str, default="2000", helptxt="The memory to reserve (--mem).")
    slurm_builder.add_control_arg(cmd_var="outfiles", vartype=str, helptxt="The name of the log and error files "
                                  "(--output and --err).  This will use the same name for both files, with the extensions .log and .err.")
    slurm_builder.add_slurm_arg(cmd_var="log", vartype="str", slurm_var="output", helptxt="The name of the stdout log "
                                "file (--output).  Do not use this together with the outfiles option.")
    slurm_builder.add_slurm_arg(cmd_var="err", vartype="str", slurm_var="error", helptxt="The name of the stderr error "
                                "file (--error).  Do not use this together with the outfiles option.")
    slurm_builder.add_slurm_arg(cmd_var="time", vartype=str, default="3-00:00:00", helptxt="The maximum walltime "
                                "allowed for the job (--time).")
    slurm_builder.add_slurm_arg(cmd_var="begin", vartype=str, default="now+5minutes", helptxt="The time to start the "
                                "script.  By default, 5 minutes after submission to avoid overloading the scheduler.")

    slurm_builder.add_control_arg(cmd_var="no_execute", vartype=bool, action="store_true", helptxt="Do not execute "
                                  "the script; just make the script file.")
    slurm_builder.add_control_arg(cmd_var="no_cleanup", vartype=bool, action="store_true", helptxt="Do you want to "
                                  "delete the script after it is submitted?  If sbatch submission fails, the script "
                                  "will NOT be deleted.  If your job fails for other reasons, the script still get deleted.")
    slurm_builder.add_control_arg(cmd_var="command", vartype=str, helptxt="The job's command: in other words what you "
                                  "would type into a bash shell to run it normally.  Surround with single quotes or "
                                  "use backslahes to escape symbols to make sure it is parsed correctly.  The variable "
                                  "$file will be populated from --arraygen, when the latter is used.")

    # Array variable stuff
    slurm_builder.add_slurm_arg(cmd_var="array", vartype=str, always_include=False, helptxt='Enter the number of '
                                'array elements to include.  For example, an array with 10 subjobs numbered 1-10 '
                                'should be given --array 1-10.  If you include this without --arraygen (i.e. array '
                                'of numbered elements), you must put "%a" in --outfiles/--log/--err and "$job" in '
                                '--command.  If --arraygen is included, --array can be autogenerated, or alternatively '
                                'a subset of indices to run can be specified (useful to repeat specific array indices).'
                                '  In the latter case, the indices start at 0.', array_var=True)
    slurm_builder.add_control_arg(cmd_var="arraygen", vartype=str, helptxt='Specify what files to loop over in the '
                                  'array.  For example, set to "*.pdb" or "mydir/*.pdb".  Surround with single quotes '
                                  'to avoid shell expansion.  Use "$file" in your --command parameter to reference the '
                                  'current file from arraygen.', array_var=True)
    slurm_builder.add_control_arg(cmd_var="arrayformat", vartype=str, helptxt='Specify bash code to format the array '
                                  'strings.  For example, to remove the pdb extension, set to ${arr[$job]%%.pdb} .  If '
                                  'left out, the default is to use the array elements unmodified.  You must use $arr '
                                  'and $job as the array and array element variable names.')
    slurm_builder.add_control_arg(cmd_var="sleep", vartype=int, helptxt="Add a sleep command before running the main "
                                  "command when running arrays.  The delay time will be the value given, in seconds, times the array ID.  For example, if you give --sleep 5, the array job with index "
                                  "123 will be delayed 615 seconds (123 * 5).", array_var=True)

    return slurm_builder

"""
# This function creates and returns the SLURM script as a list, where each list item is a line in the file.
# It uses the command line arguments (args) and the list of tuples to figure out what to do with it all.
def make_script(args, key):
    # Add the #! and --export=ALL.
    script = ['#!/bin/bash\n', '#SBATCH --export=ALL\n']

    # Loop over all arguments in the key.
    for argnum in range(len(key)):
        # Do not add a line unless we have processed this variable and switched the flag on addline.
        addline = False
        # If this is a "regular" variable that takes an argument, process it this way.
        if key[argnum][5] == 'regular':
            line = "#SBATCH --" + key[argnum][1] + " " + str(getattr(args, key[argnum][0])) + "\n"
            addline = True
        # If this is an "array" variable, process it only if usearray is given.
        if key[argnum][5] == 'array' and args.usearray:
            line = "#SBATCH --" + key[argnum][1] + " " + str(getattr(args, key[argnum][0])) + "\n"
            addline = True
        # If this is a "boolean" variable that shows up or not in the SLURM script, but doesn't take an argment, process this way.
        if key[argnum][5] == 'boolean':
            if getattr(args, key[argnum][0]) is True:
                line = "#SBATCH --" + key[argnum][1] + "\n"
                addline = True

        # If we processed the line for this variable, add it to the script list of lines.
        if addline is True:
            script.append(line)

    # If we are using arrays, add the definition of job.  Also add a delay to avoid starting all processes at the same time.
    if args.array is not None:
        script.append("job=$SLURM_ARRAY_TASK_ID\n")
        if args.sleep != 0:
            script.append("sleep $( expr " + str(args.sleep) + " \* $SLURM_ARRAY_TASK_ID )\n")

    # Add the command line to the bottom of the script.  If using a "special" array, run it with srun.
    if args.usearray and args.arraygen is not None:
        script.append("arr=(" + args.arraygen + ")\n")
        script.append("file=" + args.arrayformat + "\n")
        script.append("srun " + args.command + "\n")
    else:
        script.append(args.command + "\n")

    return(script)

# Write all the data in script to the file scriptname.
def write_script(script, scriptname):
    outfile = open(scriptname, 'w')
    for line in script:
        outfile.write(line)
    outfile.close()
"""

def main(argv):
    """
    main()
    """

    # Create a SlurmBuilder
    slurm_builder = build_slurm()
    # Have slurm_builder process arguments
    args = slurm_builder.parse_args()
    # Have slurm_builder make a slurm script
    slurm_builder.write_script


    # Setup a list of tuples.  Each tuple should contain:
    # (0 arg.varname, 1 SLURM variable name, 2 variable type, 3 default, 4 required, 5 class)
    # class should be 'regular' for SLURM parameters that receive an argument, 'boolean' for those that either appear or do not,
    # 'array' for array-related arguments, 'other' for other types of arguments.
    varkey = gen_varkey()

    # Generate the argument list using argparser
    args = gen_argparser(argv, varkey)

    # Validate arguments
    validate(args)

    # Generate "logical defaults" based on the input arguments.
    procargs = arg_logic(args, varkey)

    # Process the arguments and generate the slurm script.
    slurm_script = make_script(procargs, varkey)

    # Print the script to screen.
    for line in slurm_script:
        print(line),

    # Make a filename from the jobname, and then write the script.
    scriptname = 'tmp_' + args.job + '.sh'
    write_script(slurm_script, scriptname)

    # If desired, execute the script.  Keep the error code stored in code_sbatch.
    code_sbatch = 0
    if args.execute is True:
        # Run the script, waiting for it to finish.
        code_sbatch = subprocess.call(['sbatch', scriptname])
        # subprocess.call(['cat', scriptname])

    # If desired, cleanup the script.
    # Only do this if code_sbatch is 0, which means that sbatch completed without an error.  Scripts that fail to submit won't be deleted for later re-submission.
    if args.cleanup is True and code_sbatch == 0:
        # Delete the script.
        os.remove(scriptname)


if __name__ == "__main__":
    main(sys.argv[1:])
