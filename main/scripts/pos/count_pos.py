import argparse
import json

__author__ = 'jena'

NOUNS=['na', 'ni']

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('lexicon')
    args = parser.parse_args()

    with open(args.lexicon,'r') as fin:
        lexicon = json.load(fin)

    pos_bylength = {}

    for lexid, lexitem in lexicon.items():
        pos = lexitem['pos'].split('.')
        if len(pos) not in pos_bylength:
            pos_bylength[len(pos)] = {}
        if lexitem['pos'] in pos_bylength[len(pos)]:
            pos_bylength[len(pos)][lexitem['pos']].append((lexid,lexitem))
        else:
            pos_bylength[len(pos)][lexitem['pos']] = [(lexid,lexitem)]


    tot = 0
    sub = 0
    for vs in pos_bylength[2]:
        p,d = vs.split('.')
        if p in NOUNS:
            tot += len(pos_bylength[2][vs])
            if d == 'pl' or d == 'obv' or d == 'poss' or d == '3poss' or d == 'loc':
                print (vs, len(pos_bylength[2][vs]))
                sub += len(pos_bylength[2][vs])

    print('sub:',sub)
    print('tot:',tot)


main()
