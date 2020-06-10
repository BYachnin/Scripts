#!/usr/bin/python3
"""
slurmit.py is a script used to submit jobs to a SLURM processor automatically.
"""

from typing import List

import argparse
import glob
import os
import subprocess
import sys

# This is an exception class to catch Argument errors.
class ArgError(Exception):
    """
    Exception class for invalid Arguments.
    """
    def __init__(self, msg):
        self.msg = msg
        print(self.msg)


class SlurmArgument:
    """
    This is a class that holds data on a SLURM argument that can be extracted from an ArgParse context
    """

    def __init__(self, slurm_var: str, cmdvar: str, vartype: type, default=None, always_include: bool = True,
                 booltype: bool = False) -> str:
        """
        Initialization of SlurmArgument

        :param slurm_var: The name of the SLURM variable.  For example, cups-per-task.
        :param cmdvar: The name of the argparser variable name containing this value.
        :param vartype: The type of the variable, as seen by the argparser.
        :param default: The default value for this SLURM variable, defaults to None.
        :param always_include: Include this variable in the script even if it's not passed in, defaults to False.
        :param booltype: If True, the argument will be processed in "booltype" mode (present with no arg if arg is
        True, not present if arg is False).  Doesn't work with always_include.
        :return: A #SBATCH line for the current variable.
        """

        self.slurm_var = slurm_var
        self.cmdvar = cmdvar
        self.vartype = vartype
        self.default = default
        self.always_include = always_include
        self.booltype = booltype


    def generate_slurmtxt(self, value) -> str:
        """
        Generate the string for a SLURM variable line.

        :param value: The value to assign to the SLURM variable.
        :return: Text for a SLURM script line from this variable using value.
        """

        line = None
        # In booltype mode, if True, add the line with no argument
        if self.booltype:
            if value is True:
                line = "#SBATCH --" + self.slurm_var
        else:
            # If always_include or if we've set a non-default value, add the line
            if self.always_include or (value != self.default):
                line = "#SBATCH --" + self.slurm_var + " " + str(value)
                return line

        return line


class SlurmBuilder:
    """
    Class to manage argument parser and SlurmArguments
    """

    def __init__(self):
        """
        init
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
                        required: bool = False, helptxt: str = "", array_var: bool = False):
        """
        Add an execution control (i.e. not SLURM) argument to self.parser.

        :param cmd_var: command-line argument name
        :param vartype: argparse data type that will be passed to this variable
        :param default: The default value for the variable, as seen by argparser
        :param choices: A list of choices allowed for this argument
        :param action: The argparser "action" for this variable, defaults to "store"
        :param required: Make the argument required by argparser.
        :param helptxt: The argparser help text.
        :param array_var: Argument will be passed to the array argument_group instead of the main parser.
        """

        # Catch passing choices if action != 'store'
        if action != "store" and choices is not None:
            raise ValueError("Passing in choices with action is not default is prohibited.")

        # Add the argument to the argparser
        if array_var:
            if action == "store":
                self.array_group.add_argument("--" + cmd_var, help=helptxt, type=vartype, action=action,
                                              default=default, choices=choices, required=required)
            else:
                self.array_group.add_argument("--" + cmd_var, help=helptxt, action=action, default=default,
                                              required=required)
        else:
            if action == "store":
                self.parser.add_argument("--" + cmd_var, help=helptxt, type=vartype, action=action, default=default,
                                         choices=choices, required=required)
            else:
                self.parser.add_argument("--" + cmd_var, help=helptxt, action=action, default=default,
                                         required=required)


    def add_slurm_arg(self, cmd_var: str, vartype: type, slurm_var: str = None, default=None,
                      choices: List = None, action: str = "store", required: bool = False, always_include: bool = True,
                      booltype: bool = False, helptxt: str = "", array_var: bool = False):
        """
        Add a slurm-type argument to self.slurmargs and self.parser (by calling self.add_control_arg).

        :param cmd_var: command-line argument name
        :param vartype: argparse data type that will be passed to this variable
        :param slurm_var: The SLURM variable name.  Defaults to cmd_var if not given.
        :param default: The default value for the variable, as seen by argparser.
        :param choices: A list of choices allowed for this argument
        :param action: The argparser "action" for this variable, defaults to "store"
        :param required: Make the argument required by argparser.
        :param always_include: If True, this will be added to the sbatch script regardless of whether a value is
        passed.  If False, it will only be included if a non-default value is passed in.
        :param booltype: If True, the argument will be processed in "booltype" mode (present with no arg if arg is
        True, not present if arg is False).
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

        # always_include and booltype are mututally exclusive
        if booltype and always_include:
            raise ArgError("You cannot use both booltype and always_include ({slurm_var}).".format(slurm_var=slurm_var))
        # booltype only works if vartype is bool
        if booltype and vartype != bool:
            raise ArgError("If using booltype mode, vartype must be bool ({slurm_var}).".format(slurm_var=slurm_var))

        # Add the argument to the argparser
        self.add_control_arg(cmd_var=cmd_var, vartype=vartype, helptxt=helptxt, action=action, default=default,
                             choices=choices, array_var=array_var, required=required)

        # Create a SlurmArgument
        slurm_arg = SlurmArgument(slurm_var=slurm_var, cmdvar=cmd_var, vartype=vartype, default=default,
                                  always_include=always_include, booltype=booltype)

        # Add the slurm_arg to the list
        self.slurmargs.append(slurm_arg)


    @staticmethod
    def validate(args):
        """
        This function validates the results of parsing self.parser's arguments.

        :param args: The result of self.parser.parse_args()
        """

        # If the user specifies --outfiles (identical prefixes for the log and the error files), they cannot specifiy
        # either --output or --error.
        if args.outfiles is not None and (args.log is not None or args.err is not None):
            raise ArgError('You have provided both a value for both --outfiles and --log and/or --err.  If you provide '
                           '--outfiles, you cannot provide --log or --err.')

        # --mem is input as a string, as it can be listed as an integer in MB (eg. --mem 10000) or a value with a
        # suffix (eg. --mem 10G).
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
            if args.arrayformat is not None and '$arr' not in args.arrayformat and '${arr' not in args.arrayformat:
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

        # Make sure we have a value for args.log and args.err
        if args.log is None:
            raise ArgError("Either --outfiles and --log must be specified for output logs.")
        if args.err is None:
            raise ArgError("Either --outfiles and --err must be specified for output stderr.")

        # If args.array is empty and args.arraygen is provided, figure out args.array based on the number of
        # args.arraygen files.
        if args.array is None and args.arraygen is not None:
            # Glob args.usearray
            filelist = glob.glob(args.arraygen)
            arraylen = len(filelist)
            args.array = "0-" + str(arraylen - 1)

        if args.arraygen is not None and args.arrayformat is None:
            args.arrayformat = '${arr[$job]}'

        # If args.openmode is not defined, set it according to whether requeue is set.
        # If it is defined, use whatever the user said.
        if args.openmode is None:
            if args.no_requeue:  # args.no_requeue True means we ARE adding requeue to script
                args.openmode = 'append'
            else:
                args.openmode = 'truncate'

        return args


    def parse_args(self) -> argparse.Namespace:
        """
        Parse the args from self.parser and return the args Namespace object.  Includes validation and processing steps.

        :return: The results of self.parser.parse_args after validation.
        """

        args = self.parser.parse_args()

        self.validate(args)
        args = self.process(args)

        return args


    def write_slurm_script(self, args: argparse.Namespace, scriptname: str = None):
        """
        Process the args through the list of SlurmArguments to get a SLURM submission script.

        :param args: An argparse object
        :param scriptname: The filename for the output script.  If None, just print script to screen.
        """

        # Write the first two lines of the script
        script = ['#!/bin/bash', '#SBATCH --export=ALL']

        # Loop over self.slurmargs and add each one in turn to the script
        for s_arg in self.slurmargs:
            arg_value = args.__dict__[s_arg.cmdvar]
            slurmtxt = s_arg.generate_slurmtxt(arg_value)
            if slurmtxt:
                script.append(slurmtxt)

        # Add the echo lines for log diagnostics
        script.append('echo "python3: " `which python3`')
        script.append('echo "pythonpath: " ${PYTHONPATH}')
        script.append('echo "hostname: " ${HOSTNAME}')
        script.append('echo "PWD: " $PWD')

        # If we are using arrays, add the definition of job.
        # Also add a delay to avoid starting all processes at the same time.
        if args.array is not None or args.arraygen is not None:
            script.append("job=$SLURM_ARRAY_TASK_ID")

            if args.sleep:
                script.append("sleep $( expr " + str(args.sleep) + " \* $SLURM_ARRAY_TASK_ID )")

        # Add the command line to the bottom of the script.  If using a "special" array, run it with srun.
        if args.arraygen is not None:
            script.append("arr=(" + args.arraygen + ")")
            script.append("file=" + args.arrayformat)
            script.append("srun " + args.command)
        else:
            script.append(args.command)

        # Print the script to screen.
        for line in script:
            print(line)

        # Add newlines to the end of each line in script.
        script = [line + "\n" for line in script]

        # Write all the data in script to the file scriptname.
        if scriptname is not None:
            with open(scriptname, "w") as outfile:
                outfile.writelines(script)


def build_slurm() -> SlurmBuilder:
    """
    This function creates a SlurmBuilder with relevant argparse arguments set up.

    :return: A completely initiazed SlurmBuilder with arguments.
    """

    slurm_builder = SlurmBuilder()
    slurm_builder.add_slurm_arg(cmd_var="job", vartype=str, slurm_var="job-name", required=True, helptxt="The "
                                "SLURM name for your job (--job-name).  Will be used to generate log/err filenames if "
                                "not given, in which case it will genereate the files in the current directory.")
    slurm_builder.add_slurm_arg(cmd_var="partition", vartype=str, default="main", helptxt="The "
                                "SLURM partition to run on (--partition).")
    slurm_builder.add_slurm_arg(cmd_var="no_requeue", vartype=bool, slurm_var="requeue", action="store_false",
                                always_include=False, booltype=True, default=True,
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
                                  "(--output and --err).  This will use the same name for both files, with the "
                                  "extensions .log and .err.")
    slurm_builder.add_slurm_arg(cmd_var="log", vartype=str, slurm_var="output", helptxt="The name of the stdout log "
                                "file (--output).  Do not use this together with the outfiles option.")
    slurm_builder.add_slurm_arg(cmd_var="err", vartype=str, slurm_var="error", helptxt="The name of the stderr error "
                                "file (--error).  Do not use this together with the outfiles option.")
    slurm_builder.add_slurm_arg(cmd_var="time", vartype=str, default="3-00:00:00", helptxt="The maximum walltime "
                                "allowed for the job (--time).")
    slurm_builder.add_slurm_arg(cmd_var="begin", vartype=str, default="now+5minutes", helptxt="The time to start the "
                                "script.  By default, 5 minutes after submission to avoid overloading the scheduler.")

    slurm_builder.add_control_arg(cmd_var="no_execute", vartype=bool, action="store_true", helptxt="Do not execute "
                                  "the script; just make the script file.")
    slurm_builder.add_control_arg(cmd_var="no_cleanup", vartype=bool, action="store_true", helptxt="Do you want to "
                                  "delete the script after it is submitted?  If sbatch submission fails, the script "
                                  "will NOT be deleted.  If your job fails for other reasons, the script still get "
                                  "deleted.")
    slurm_builder.add_control_arg(cmd_var="command", vartype=str, helptxt="The job's command: in other words what you "
                                  "would type into a bash shell to run it normally.  Surround with single quotes or "
                                  "use backslahes to escape symbols to make sure it is parsed correctly.  The variable "
                                  "$file will be populated from --arraygen, when the latter is used.", required=True)

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
                                  "command when running arrays.  The delay time will be the value given, in seconds, "
                                  "times the array ID.  For example, if you give --sleep 5, the array job with index "
                                  "123 will be delayed 615 seconds (123 * 5).", array_var=True)

    return slurm_builder


def main(argv):
    """
    main()
    """

    # Create a SlurmBuilder
    slurm_builder = build_slurm()
    # Have slurm_builder process arguments
    args = slurm_builder.parse_args()

    # Make a filename from the jobname, and then write the script.
    scriptname = 'tmp_' + args.job + '.sh'
    # Have slurm_builder make a slurm script from parsed args
    slurm_builder.write_slurm_script(args, scriptname)

    # If desired, execute the script.  Keep the error code stored in code_sbatch.
    code_sbatch = 0
    if args.no_execute is not True:
        # Run the script, waiting for it to finish.
        try:
            code_sbatch = subprocess.call(['sbatch', scriptname])
        except FileNotFoundError:
            raise FileNotFoundError("sbatch is not available.  Are you running in a SLURM environment?")

    # If desired, cleanup the script.
    # Only do this if code_sbatch is 0, which means that sbatch completed without an error.  Scripts that fail to
    # submit won't be deleted for later re-submission.
    if args.no_cleanup is not True and code_sbatch == 0:
        # Delete the script.
        os.remove(scriptname)


if __name__ == "__main__":
    main(sys.argv[1:])
