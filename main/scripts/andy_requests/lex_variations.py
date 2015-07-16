import argparse
import json
import re

__author__ = 'jena'

def add_to_dict_of_dict(d,k,k2,v):
    if k not in d:
        d[k] = {}
    if k2 not in d[k]:
        d[k][k2] = []
    d[k][k2].append(v)


def word_distance(ph,ph2):
    if len(ph) == len(ph2):
        long_string = ph
        short_string = ph2
    else:
        long_string = max([ph,ph2], key=len)
        short_string = min([ph,ph2], key=len)

    l_long_string = long_string.strip().split(' ')
    l_short_string = short_string.strip().split(' ')

    count = 0.0

    for word in l_short_string:
        if word in l_long_string:
            count += 1.0

    return float(count)/float(len(l_short_string))

def match_by_gloss(lexicon,lexid,h_lexid):
    # exact gloss match : BEST CASE SCENARIO
    if 'gloss' in lexicon[h_lexid] and lexicon[lexid]['gloss'] == lexicon[h_lexid]['gloss']:

        # exact match type
        # high confidence
        return 0,1  #type 0 confidence 1

    # make some changes to glosses
    else:
        # to the glottal stop gloss
        gloss = re.sub(r'[,|/|(|)|;]', ' ',lexicon[lexid]['gloss'])
        gloss = gloss.replace('oneself','self')
        gloss = gloss.replace('something','s.t.')
        gloss = gloss.replace('someone','s.o.')
        gloss = re.sub('(^| )a ',' ',gloss)
        gloss = re.sub('(^| )the ',' ',gloss)
        gloss = re.sub('(^| )to ',' ',gloss)
        gloss = re.sub(r' +',' ',gloss)

        # to the h-lexical item gloss
        if 'gloss' in lexicon[h_lexid]:
            h_gloss = re.sub(r'[,|/|(|)|;]', ' ',lexicon[h_lexid]['gloss'])
            h_gloss = h_gloss.replace('oneself','self')
            h_gloss = h_gloss.replace('something','s.t.')
            h_gloss = h_gloss.replace('someone','s.o.')
            h_gloss = re.sub('(^| )a ',' ',h_gloss)
            h_gloss = re.sub('(^| )the ',' ',h_gloss)
            h_gloss = re.sub('(^| )to ',' ',h_gloss)
            h_gloss = re.sub(r' +',' ',h_gloss)
        else:
            h_gloss = ''

        # TRIAL 2 Match: By gloss again
        if gloss == h_gloss or h_gloss in gloss or gloss in h_gloss:
            # contains match
            # high confidence match



            return 1,1  #type 1 confidence 1


        # TRIAL 3 Match: By Word distance
        else:
            d = word_distance(gloss,h_gloss)
            if d > 0.5:
                # contains match
                # high confidence matches
                return 1,1  #type 1 confidence 1



            elif d > 0.0:

                # print("%s %s"%(lexid,h_lexid))
                # print(d)
                # print(lexid, lexicon[lexid]['lex'], lexicon[lexid]['pos'], gloss)
                # print(h_lexid, lexicon[h_lexid]['lex'], lexicon[lexid]['pos'], h_gloss ,'\n')

                # need to manually look at
                # mid confidence matches
                return 2,2  #type 2 confidence 2

            else:
                # need to manually look at
                # low confidence matches
                return 3,3


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('lexicon')
    args = parser.parse_args()

    with open(args.lexicon) as fin:
        lexicon = json.load(fin)

    h_initial = {}
    glottal_initial = {}

    for lexid, lexitem in lexicon.items():
        lex = lexitem['lex']
        #if lex.startswith("'"):
        if lex.startswith("i") or lex.startswith("e") or lex.startswith("o") or lex.startswith("u"):
            add_to_dict_of_dict(glottal_initial,lex,lexitem['pos'],lexid)
        elif lex.startswith('h'):
            add_to_dict_of_dict(h_initial,lex,lexitem['pos'],lexid)

    matches_found = [0,0,0,0,0,0,0]


    # for each glottal initial lex
    for lex in glottal_initial:
        # for each pos of the glottal initial lex
        for pos,lexids in glottal_initial[lex].items():
            h_lex = 'h'+lex[1:]

            # if the h-initial matching lex is found
            if h_lex in h_initial:

                # for each lex id of a glottal initial lex of a certain pos
                for lexid in lexids:
                    potential = []
                    match_h_lexid = None
                    match_confidence = -1

                    # multiple matches
                    if len(h_initial[h_lex]) > 1:

                        if pos in h_initial[h_lex]:
                            if len(h_initial[h_lex][pos]) == 1:
                                h_lexid = h_initial[h_lex][pos][0]
                                match_type, match_confidence = match_by_gloss(lexicon,lexid,h_lexid)
                                matches_found[match_type] += 1
                            else:
                                # print('\n',lexid,'More than one potential match')
                                # print(lexid, lex, pos, lexicon[lexid]['gloss'])

                                matches_found[6]+=1 # multiple matches
                                for h_lexid in  h_initial[h_lex][pos]:
                                    potential.append(h_lexid)
                                    # print(h_lexid,lexicon[h_lexid]['lex'],lexicon[h_lexid]['pos'],lexicon[h_lexid]['gloss'])
                        else:
                            # print('\n',lexid,'More than one potential match')
                            # print(lexid, lex, pos, lexicon[lexid]['gloss'])

                            matches_found[6]+=1 # multiple matches
                            for h_pos in h_initial[h_lex]:
                                for h_lexid in  h_initial[h_lex][h_pos]:
                                    potential.append(h_lexid)
                                    # print(h_lexid,lexicon[h_lexid]['lex'],lexicon[h_lexid]['pos'],lexicon[h_lexid]['gloss'])

                    else:
                        # if exact matching pos is found
                        if pos in h_initial[h_lex]:
                            f = False

                            h_lexid = h_initial[h_lex][pos][0]
                            match_h_lexid = h_lexid

                            match_type, match_confidence = match_by_gloss(lexicon,lexid,h_lexid)
                            matches_found[match_type]+=1


                        # no pos exact match is found: NOTE there's only 1 item in the dictionary
                        else:
                            h_pos = list(h_initial[h_lex].keys())[0]
                            match_h_lexid = h_initial[h_lex][h_pos][0]
                            match_confidence = 4

                            matches_found[4]+=1 # pos mismatches



            else:
                matches_found[5]+=1  # no matches


    print (matches_found)

main()