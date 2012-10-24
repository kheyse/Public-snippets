#!/usr/bin/env python

import sys
import getopt
import itertools

#iterator yielding each element together with the next element
def pairwise(iterable):
    "s -> (s0,s1), (s1,s2), (s2, s3), ..."
    a, b = itertools.tee(iterable)
    next(b,None)
    return itertools.izip(a, b)

def usage():
    print """usage: table2csv --help
       table2csv [-t<int>] [-d<char>] [file]
-t, --tab-expand <int>: expand tabs in input to <int> spaces (default: 4)
-d, --delimiter <char>: delimiter used in csv file (default: ,)
file: input file to be converted to csv. if none provided, input is read from standard input"""

def main():
    delimiter = ','
    tab_expand = 4
    input = sys.stdin
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hd:t:", ["help", "delimiter=", "tab-expand="])
    except getopt.GetoptError, err:
        print str(err)
        usage()
        sys.exit(2)
    for o, a in opts:
        if o == "-v":
            verbose = True
        elif o in ("-h", "--help"):
            usage()
            sys.exit()
        elif o in ("-d", "--delimiter"):
            delimiter = a
        elif o in ("-t", "--tab-expand"):
            tab_expand = int(a)
        else:
            assert False, "unhandled option"
    if len(args)>1:
        usage()
        sys.exit(2)
    if args:
        input = open(args[0])

    lines = input.readlines()
    lines = map(lambda s:s.expandtabs(tab_expand), lines)
    lines = map(lambda s:s.rstrip('\n\r'), lines)
    maxlen = reduce(max,map(len,lines))
    
    #calculate which character columns contain only spaces
    spaces = []
    for p in xrange(maxlen):
        for l in lines:
            if p<len(l):
                if l[p]!=' ':
                    spaces.append(False)
                    break
        else:
            spaces.append(True)
    
    #a run of spaces may separate two columns
    for i in xrange(len(spaces)-1):
        if spaces[i+1]:
            spaces[i] = False
            
    #trailing spaces don't mark a column
    spaces.pop(-1)
    
    #convert spaces into column widths
    columns = [0]+[i+1 for i,v in enumerate(spaces) if v]+[maxlen]
    #print spaces, columns
    for l in lines:
        elms = ['"%s"'%l[start:stop].rstrip().replace('"','""') for start,stop in pairwise(columns)]
        print delimiter.join(elms)
    
if __name__=='__main__':
    main()
    