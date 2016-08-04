from pymol import cmd

#To be run from within pymol
#You can use "run rmsd_score_table.py" from the pymol terminal.
#More likely, you want to run it from the command line, like so:
#pymol -qc rmsd_score_table.py

#Change these four variables to match your specific case
rmsdroot = "pdb_file_to_compare_to.pdb"
selector = "pymol selector for use in the RMSD calculation eg. chain a and resi 1-100 and name ca"
outname = "output_score_table_name.csv"
scores = ['total_score','cstE','ligE']			#List of score terms to include in the output csv table.  These should be exactly as seen in the output PDB footer.

header = []
header.extend(scores)
header.append("rmsd")
header.append("description")
outfile = open(outname, "a")
outfile.write(', '.join(header))
outfile.write('\n')

cmd.load(rmsdroot, "root")
for filename in sorted(os.listdir(os.getcwd())):
	score_vals = []
	if filename.endswith(".pdb"):
		cmd.load(filename, "decoy")
	else: continue
	rmsd = cmd.rms_cur("root and "+selector, "decoy and "+selector)
	
	lines=open(filename).readlines()
	for score_term in scores:
		for line in reversed(lines):
			if line.startswith('#'):# assumes all score terms are at the end of the file, no comments after them
				sys.exit(score_term+" was not found in "+filename)
			(this_term, score)=line.split()[:2]
			if this_term==score_term:
				score_vals.append(score)
				break
	
	score_vals.append(rmsd)
	score_vals.append(filename)
	
	outfile.write((', ').join(map(str, score_vals)))
	outfile.write('\n')
	cmd.delete("decoy")

outfile.close()
