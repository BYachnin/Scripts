#!/usr/bin/env python
import sys

def main(args):
    infile=args[1]
    if len(args) == 3:
        offset=int(args[2])
    else:
        offset=1

    fh = open( infile, "r" )
    nextline = fh.readline()
    
    motifWidth = len(nextline.strip())
    
    weightMatrix = [{
                    'A':0.0,'C':0.0,'D':0.0,'E':0.0,'F':0.0,
                    'G':0.0,'H':0.0,'I':0.0,'K':0.0,'L':0.0,
                    'M':0.0,'N':0.0,'P':0.0,'Q':0.0,'R':0.0,
                    'S':0.0,'T':0.0,'W':0.0,'Y':0.0,'V':0.0
                    } for k in range(motifWidth)]
    
    while nextline:
        for k in range(motifWidth):
            weightMatrix[k][nextline[k]] += 1
        nextline = fh.readline()

    sums = [ sum( weightMatrix[k].values() ) for k in range(motifWidth) ];

    if sums[0] == 0.0:
        freqMatrix = [dict(( key , val) for (key,val) in weightMatrix[k].iteritems() )
                    for k in range(motifWidth)]
    else:
        freqMatrix = [dict(( key , val/sums[k]) for (key,val) in weightMatrix[k].iteritems() )
                    for k in range(motifWidth)]
    
    tokens=infile.rsplit('.',1)
    file=tokens[0]
    outfile= '%s.transfac' % (file)

    transfac = open(outfile,"w")
            
    transfac.write("ID Matrix\nPO")
    
    for key,val in freqMatrix[1].iteritems():
        transfac.write("\t" + key)
    
    transfac.write("\n")
    
    for k in range(motifWidth):
        transfac.write(str(k+offset))
        
        for key,val in freqMatrix[k].iteritems():
            transfac.write("\t")
            transfac.write("%0.4f" %val)
            
        transfac.write("\n")

if __name__ == "__main__":
    #infile = '/Users/arubenstein/Downloads/sorted_complete.txt'
    #outfile = '/Users/arubenstein/Dropbox/Research/Khare Lab/Mean Field/Design/HCV.transfac'
    
    main(sys.argv)
