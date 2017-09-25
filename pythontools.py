#Usage pullscores(pdbfile.pdb, output.csv, scoreterm1, scoreterm2, scoreterm3, ....)
#Pulls the listed scoreterms from the pdbfile.pdb, and outputs them to output.csv.
#NOT TESTED
def pullscores(*arg):
	#Set up filenames
	pdbfilename = arg[0]
	outputfilename = arg[1]
	#Remove the filenames from arg.  What's left is the list of scoreterms.
	arg.remove(arg[0])
	arg.remove(arg[1])
	#Open the pdb file for reading, and the output file for writing.
	pdbfile = open(pdbfilename, 'r')
	outputfile = open(outfilename, 'a')
	
	score_vals=[]
	
	#Loop over each requested scoreterm
	for score_term in arg:
		for pdbline in reversed(readlines(pdbfile)):
			if pdbline.startswith('#'): #assumes all score terms are at the end of the file, no comments after them
				print "WARNING: The scoreterm " + score_term + " was not found in the PDB file " + pdbfilename
				break
			#Split the current line into scoreterm name and score.
			(this_term, score)=pdbline.split()[:2]
			#If we match the score term.
			if this_term==score_term:
				#Add the score term to the list of score values.
				score_vals.append(score)
				break
				
	outfile.write((', ').join(map(str, score_vals)))
	outfile.write('\n')
	outfile.close()
	return;
	
#Usage: scorebyres(pdbfile.pdb, scoreterm="total_score", outfilename="")
#The score for each residue in pdbfile.pdb is read in.  It is stored in a list of lists.
#The inner list contains the residue identified in position 0 and the score in position 1.
#The outer list contains one inner list per residue in the PDB file.
#The outer list is returned.
#If outfile is provided, writes the resulting list to file.
def scorebyres(pdbfilename, scoreterm="total", outfilename=""):
	#Open the file for reading, as a list of lines.
	pdbfile = open(pdbfilename, 'r').readlines()
	
	#Remove lines up to the beginning of the pose energies table.
	while True:
		if pdbfile[0].startswith('#BEGIN_POSE_ENERGIES_TABLE'): break
		pdbfile.remove(pdbfile[0])
		
	#Remove lines after the end of the pose energies table.
	while True:
		curlength = len(pdbfile) - 1
		if pdbfile[curlength].startswith('#END_POSE_ENERGIES_TABLE'): break
		pdbfile.remove(pdbfile[curlength])
	
	#Convert each line into a list, using whitespace as the delimiter.  Place this into the scoretable list.
	scoretable = []
	for pdbline in pdbfile:
		scoretable.append(pdbline.split())
		
	#Search for scoreterm in the label row.
	#First, fine the label row number.
	for lineidx in range(len(scoretable)):
		if scoretable[lineidx][0] == 'label':
			#Now go through each item in that row.  Store the scoreterm row as scoretermcol.
			for colidx in range(len(scoretable[lineidx])):
				if scoretable[lineidx][colidx] == scoreterm:
					scoretermcol = colidx
					break

	#Now, go through the scoretable again.  Pull out the residue identifier and the desired scoreterm and put in a list, reslist.  Skip the leading and ending rows.
	reslist = []
	for lineidx in range(len(scoretable)):
		if (scoretable[lineidx][0].startswith('#') or scoretable[lineidx][0].startswith('label') or scoretable[lineidx][0].startswith('weights') or scoretable[lineidx][0].startswith('pose')): continue
		reslist.append([scoretable[lineidx][0], scoretable[lineidx][scoretermcol]])
		
	#If outfilename is given, set up a file for output.
	if (outfilename != ""):
		outfile = open(outfilename, 'w')
	
		for idx in range(len(reslist)):
			outfile.write(','.join(map(str,reslist[idx])))
			outfile.write('\n')
	
	#Return the reslist.
	return reslist;
				
	
#Usage: compare_scorebyres(pdbfile.pdb, scoreterm="total", compare="", threshold=0, outfilename="")
#Pulls a specific scoreterm for each residue in a PDB file.  By default, this is total_score.
#If compare is specified, it computes (pdbfile score - compare pdb score), and outputs this.
#If threshold is set, only those deltas whose absolute values are greater than threshold will be output.

def compare_scorebyres(pdbfile, scoreterm="total", compare="", threshold=0, outfilename=""):
	#Create scoreterm lists for the two pdbfiles.
	mainlist = scorebyres(pdbfile, scoreterm)
	if (compare != ""):
		comparelist = scorebyres(compare, scoreterm)
			
		if (len(mainlist) != len(comparelist)):
			print "WARNING: The two lists have different numbers of residues in the score table."
			print "You may not get the results you expect."
		
		#Create the output list.
		outlist = []
		#Loop over each item in the lists.
		for idx in range(len(mainlist)):
			#Calculate the difference
			delta = float(mainlist[idx][1]) - float(comparelist[idx][1])
			#If the difference is greater than the threshold difference, add this to a new list.
			if (threshold == 0) or (abs(delta) > threshold):
				outlist.append([mainlist[idx][0],delta])
	
	#Otherwise, just make the outlist mainlist.
	else:
		outlist = mainlist
		
	#If outfilename is given, set up a file for output.
	if (outfilename != ""):
		outfile = open(outfilename, 'w')
	
		for idx in range(len(outlist)):
			outfile.write(','.join(map(str,outlist[idx])))
			outfile.write('\n')
		outfile.close()
			
	return outlist;
	
#Usage: codopt(protein_sequence_string, dictionary_of_codons)
#This function uses codon_tools to reverse translate a protein sequence back to DNA.  The DNA sequence is returned as a string.
#usable_codons can be passed to create a custom set of codons to use.
#Otherwise, a default codon table containing common E. coli codons is used.
def codopt(protein_string, usable_codons = {  'A':['GCA', 'GCC', 'GCG'], 'R':['CGT', 'CGC'], 'N':['AAC', 'AAT'], 'D':['GAC', 'GAT'], 'C':['TGC', 'TGT' ], 'Q':['CAA', 'CAG'], 'E':['GAA'], 'G':['GGC', 'GGT'], 'H':['CAC', 'CAT'], 'I':['ATC', 'ATT'], 'L':['CTC', 'CTG', 'CTT', 'TTA', 'TTG'], 'F':['TTT', 'TTC'], 'P':['CCA', 'CCG', 'CCT'], 'S':['AGC', 'TCC','TCT'], 'T':[ 'ACT', 'ACC', 'ACG' ], 'Y':['TAC', 'TAT'], 'V':['GTA', 'GTC', 'GTG', 'GTT'], 'W':['TGG'], 'M':['ATG'], 'K':['AAA', 'AAG'], '*':['TAA', 'TAG', 'TGA']}):
	#Import modules
	from Bio.Seq import Seq
	from Bio.Alphabet import generic_protein
	from codon_tools import FopScorer, CodonOptimizer
	
	#Define a codon scorer that uses the codon frequency table above.
	scorer = FopScorer(opt_codons = usable_codons)
	#Define an optimizer based on scorer
	opt = CodonOptimizer(scorer)
	
	#Create a sequence object from the protein_string
	protein_seq = Seq(protein_string, generic_protein)
	#Randomly reverse translate the sequence.
	randdnaseq = opt.random_reverse_translate(protein_seq)
	#Now codon optimize.
	dnaseq = opt.hillclimb(randdnaseq)
	
	#Assert that the dnaseq matches the original protein sequence.
	assert str(Seq.translate(dnaseq[0])) == str(protein_seq)
	
	#Convert dnaseq to a string and return.
	return(str(dnaseq[0]))