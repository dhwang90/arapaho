from collections import OrderedDict
import glob
import os
import argparse
import re

__author__ = 'jena'

def get_text(line):
    l = line.split(' ')
    return ' '.join(l[1:])

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('document_path')
    args = parser.parse_args()

    docpath = args.document_path

    lines_cnt = 0
    words = 0
    morpheme = 0

    wpl = 0.0
    mpw = 0.0

    for file in glob.glob(os.path.join(docpath,"*.txt")):
        with open(file) as fin:
            for line in fin:
                if line.startswith('\\ref '):
                    lines_cnt += 1
                elif line.startswith('\\tx '):
                    l = re.split(r'\s+',line)
                    words += len(l) -2
                elif line.startswith('\\mb '):
                    l = re.split(r'\s+',line)
                    morpheme += len(l) -2

    print ('lines: %s'%lines_cnt)
    print ('words: %s'%words)
    print ('morphemes: %s'%morpheme)

    print('words per line: %.2f'%(float(words)/float(lines_cnt)))
    print('morpheme per word: %.2f'%(float(morpheme)/float(words)))


main()