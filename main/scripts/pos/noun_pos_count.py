import argparse
import json
import re


__author__ = 'jena'

NOUNS=['na', 'ni']

PLURAL_TYPE_1 = re.compile(r'[bw3tsncykx\'h]o\'?$')  # Co' for NA, Co for NI
PLURAL_TYPE_2 = re.compile(r'(ii|uu)$')  # ii/uu endings
PLURAL_TYPE_3 = re.compile(r'\'(i|u)$')  # 'i/'u endings

def get_nouns(pos_bylength):
    pos_base = {}
    for pos in pos_bylength[1]:
        if pos in NOUNS:
            if pos not in pos_base:
                pos_base[pos] = []
            pos_base[pos].extend(pos_bylength[1][pos])

    pos_deriv = {}
    for p in pos_bylength[2]:
        pos,deriv = p.split('.')
        if pos in NOUNS:
            if deriv not in pos_deriv:
                pos_deriv[deriv] = []
            pos_deriv[deriv].extend(pos_bylength[2][p])

    return pos_base, pos_deriv


def by_length(lexicon):
    pos_bylength = {}

    for lexid, lexitem in lexicon.items():
        pos = lexitem['pos'].split('.')
        if len(pos) not in pos_bylength:
            pos_bylength[len(pos)] = {}
        if lexitem['pos'] in pos_bylength[len(pos)]:
            pos_bylength[len(pos)][lexitem['pos']].append((lexid,lexitem))
        else:
            pos_bylength[len(pos)][lexitem['pos']] = [(lexid,lexitem)]

    return pos_bylength


def by_lex_pos(lexicon):
    pos_bylex = {}

    for lexid, lexitem in lexicon.items():
        lex = lexitem['lex']
        pos = lexitem['pos']
        if (lex,pos) not in pos_bylex:
            pos_bylex[(lex,pos)] = []
        pos_bylex[(lex,pos)].append(lexitem)

    return pos_bylex


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('lexicon')
    # parser.add_argument('out')
    args = parser.parse_args()

    with open(args.lexicon,'r') as fin:
        lexicon = json.load(fin)

    pos_by_length = by_length(lexicon)
    pos_by_lex = by_lex_pos(lexicon)

    noun_deriv_1seg,noun_deriv_2seg = get_nouns(pos_by_length) # 1seg = 1 segments

    ii_uu = 0
    na = 0
    gi_gu = 0
    t = 0

    for deriv, lexitems in noun_deriv_2seg.items():
        if deriv == 'pl':
            for lexitem in lexitems:
                t += 1
                if PLURAL_TYPE_2.search(lexitem[1]['lex']):
                    ii_uu += 1
                elif PLURAL_TYPE_3.search(lexitem[1]['lex']):
                    gi_gu += 1
                elif PLURAL_TYPE_1.search(lexitem[1]['lex']):
                    na += 1

                ## before regex...
                # if lexitem['lex'].endswith('ii') or lexitem['lex'].endswith('uu'):
                #     ii_uu += 1
                # else:
                #     if lexitem['lex'].endswith('o\'') or lexitem['lex'].endswith('o'):
                #         na += 1
                #     elif lexitem['lex'].endswith('\'i') or lexitem['lex'].endswith('\'u'):
                #         gi_gu += 1
                #     else:
                #         print(lexitem['pos'] , lexitem['lex'], lexitem['gloss'])

    print (ii_uu,na,gi_gu,ii_uu+na+gi_gu)
    print("%.2F"%(float(ii_uu+na+gi_gu)/float(t)))

main()
