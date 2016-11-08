from pymol import cmd

#To be run from within pymol
#This script will calculate the RMSD between a file (the root) and all other PDB files.
#The results will be output to a file with selected Rosetta scoreterms included as well.
#You can use "run rmsd_score_table.py" from the pymol terminal.
#More likely, you want to run it from the command line, like so:
#pymol -qc rmsd_score_table.py

#Change these four variables to match your specific case
rmsdroot = "pdb_file_to_compare_to.pdb"
selector = "pymol selector for use in the RMSD calculation eg. chain a and resi 1-100 and name ca"
outname = "output_score_table_name.csv"
scores = ['total_score','cstE','ligE']			#List of score terms to include in the output csv table.  These should be exactly as seen in the output PDB footer.

#Initialize a varaible for the header row of scoreterms.
header = []
#Add all of the scoreterms in scores to the header.
header.extend(scores)
#Add rmsd and description to the header.
header.append("rmsd")
header.append("description")

#Open outfile for writing.
outfile = open(outname, "a")
#Add the header line to outfile.
outfile.write(', '.join(header))
outfile.write('\n')

#Load the "root" PDB file (ie. the file that will be compared to all other pdb files.)
cmd.load(rmsdroot, "root")
#Iterate over all files in the directory.
for filename in sorted(os.listdir(os.getcwd())):
	#Initialize the list of scores.
	score_vals = []
	#If the file is a pdb file, load it as "decoy"
	if filename.endswith(".pdb"):
		cmd.load(filename, "decoy")
	else: continue
	#Calculate the RMSD between root and decoy over the atoms specified by selector.
	rmsd = cmd.rms_cur("root and "+selector, "decoy and "+selector)
	
	#Read the PDB file into lines.
	lines=open(filename).readlines()
	#Iterate over each scoreterm in scores.
	for score_term in scores:
		#Going backwards through the PDB file, find the line starting with the current scoreterm.
		#Exit if the scoreterm isn't found in the file.
		for line in reversed(lines):
			if line.startswith('#'):# assumes all score terms are at the end of the file, no comments after them
				sys.exit(score_term+" was not found in "+filename)
			#Split the line into the term name and the score.
			(this_term, score)=line.split()[:2]
			#If the term matches the desired scoreterm, store the score in score_vals and break (continue to next term).
			if this_term==score_term:
				score_vals.append(score)
				break
	
	#Add the rmsd and filename to score_vals to complete that line of the table.
	score_vals.append(rmsd)
	score_vals.append(filename)
	
	#Add the scores to the outfile using CSV formatting.
	outfile.write((', ').join(map(str, score_vals)))
	outfile.write('\n')
	#Delete the current decoy to make room for the next one and reduce memory footprint.
	cmd.delete("decoy")

outfile.close()
