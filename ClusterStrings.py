#!/usr/bin/python

import sys
import operator
import random

#Usage example: python ClusterStrings.py sequences.txt 5

#Input: sequences.txt simple text file where each line represents a sequence
#       The second arg is the number of sequences you wish to choose.

#Output: sequences_hamm.txt, sequences_sort.txt, sequences_rand.txt

def hamdist(str1, str2):
    diffs = 0
    for ch1, ch2 in zip(str1, str2):
        if ch1 != ch2:
            diffs += 1
    return diffs

def main(args):

    with open(args[1]) as strings:
        str_list = strings.read().splitlines()

    num_seq = int(args[2])

    tokens=args[1].rsplit('.',1)
    file=tokens[0]
    outfile_hamm = '%s%d_hamm.txt' % (file,num_seq)
    outfile_sort = '%s%d_sort.txt' % (file,num_seq)
    outfile_rand = '%s%d_rand.txt' % (file,num_seq)
    outfile_rand2 = '%s%d_rand2.txt' % (file,num_seq)

    dist_dict = { seq:hamdist(str_list[0],seq) for seq in str_list }
    sorted_hamm_t = sorted(dist_dict.items(), key=operator.itemgetter(1))
    sorted_hamm = [ key for key,val in sorted_hamm_t]
    
    random.shuffle(str_list)
    
    step = (len(str_list)-1)/(num_seq-1)
    end = len(str_list)

    selected_hamm = sorted_hamm[0:end:step]
    selected_sort = sorted(str_list)[0:end:step]
    selected_rand = str_list[0:end:step]

    random.shuffle(str_list)

    selected_rand2 = str_list[0:end:step]

    hamm_out = open(outfile_hamm,"w")
    sort_out = open(outfile_sort,"w")
    rand_out = open(outfile_rand,"w")
    rand2_out = open(outfile_rand2,"w")

    hamm_out.write("\n".join(selected_hamm))
    sort_out.write("\n".join(selected_sort))
    rand_out.write("\n".join(selected_rand))
    rand2_out.write("\n".join(selected_rand2))
if __name__ == "__main__":

    main(sys.argv)

