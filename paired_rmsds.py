from pymol import cmd
import sys

reinit

selector="decoy and name CA"	#PyMOL selector for the RMSD calculation.

pdblist = []
longstring = 0

for file in sorted(os.listdir(os.getcwd())):
	if file.endswith(".pdb"):
		cmd.load(file, "decoy")
		pdblist.append(file)	
		if len(file) > longstring: longstring = len(file)

rmslist = []
masterlist = [["bcl::storage::Table<double>"]]
masterlist[0].extend(pdblist)

for idx in range(0,len(pdblist)):
	rmslist = []
	rmslist = [pdblist[idx]]
	rmslist.extend(cmd.intra_rms_cur(selector, idx+1))
	for n,i in enumerate(rmslist):
		if i==-1.0: rmslist[n]=0
	#print rmslist
	masterlist.append( rmslist )
	
#print masterlist

rmsd_file = open("rmsds.txt", "a")
#rmsd_file.write(masterlist)

longstring = longstring + 2

firstfrmt = '{:'+str(longstring)+'s}' + len(pdblist) * ('{:>'+str(longstring)+'s}')
frmt = '{:'+str(longstring)+'s}' + len(pdblist) * ('{:>'+str(longstring)+'f}')
#print frmt

first = True

for line in masterlist:
	if (first):
		#print(firstfrmt.format(*line))
		rmsd_file.write(firstfrmt.format(*line))
		rmsd_file.write('\n')
		first = False
	else:
		#print(frmt.format(*line))
		rmsd_file.write(frmt.format(*line))
		rmsd_file.write('\n')
		
rmsd_file.close()
