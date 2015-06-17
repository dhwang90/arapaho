import argparse
import json

__author__ = 'jena'

# COPY OVER LEX FIELDS INTO APPROPRIATE FIELDS


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('lexicon')
    parser.add_argument('lexicon_out')
    args = parser.parse_args()

    deriv_labels = {'3 poss.':'poss3','loc.':'loc','obv.sg.':'obv','obv.pl.':'obv.pl','voc.':'voc'}

    with open(args.lexicon) as fin:
        lexicon = json.load(fin)

    save_lex = {}
    pos_s = []
    i = 0

    print(len(lexicon))

    for lex_id, lex_entry in lexicon.items():
        if lex_entry['language'] == 'Arapaho':
            pos = lex_entry['pos'].split('.')[0]
            changed = False

            if pos in ['na','ni'] and '.loc' not in lex_entry['pos'] and '.voc' not in lex_entry['pos'] and '.pl' not in lex_entry['pos']:
                if 'derivations' not in lex_entry:
                    lex_entry['derivations'] = {}

                # if 'senses' in lex_entry and len(lex_entry['senses'])>0 and '[' in lex_entry['senses'][0]['definition']:
                #     print (lex_id, lex_entry['lex'], '\tDEF\t', lex_entry['senses'][0]['definition'])

                deriv_adds = {}
                for deriv_type in lex_entry['derivations']:

                    if '[' in lex_entry['derivations'][deriv_type]:

                        print (lex_id, lex_entry['lex'], '\t', deriv_type)

                        dtypes = lex_entry['derivations'][deriv_type].split('[')
                        for dtype in dtypes[1:]:

                            print('\t', dtype)

                            for dlabel,true_label in deriv_labels.items():
                                if dtype.startswith(dlabel):
                                    content = dtype.replace(dlabel,'').strip(']').strip()
                                    deriv_adds[true_label] = content

                        lex_entry['derivations'][deriv_type] = dtypes[0]


                for true_label,content in deriv_adds.items():
                    if true_label not in lex_entry['derivations'] or \
                        lex_entry['derivations'][true_label] == 0:
                        lex_entry['derivations'][true_label] = content

                        print('\t ADDING',true_label.upper(), content)


                if 'pl' not in lex_entry['derivations'] or lex_entry['derivations']['pl'] == '':
                    lex_entry['derivations']['pl'] = lex_entry['lex']
                    changed = True

                if 'loc' not in lex_entry['derivations'] or lex_entry['derivations']['loc'] == '':
                    lex_entry['derivations']['loc'] = lex_entry['lex']
                    changed = True

                if pos == 'na':
                    if 'obv' not in lex_entry['derivations'] or lex_entry['derivations']['obv'].strip() == '':
                        lex_entry['derivations']['obv'] = lex_entry['lex']
                        changed = True


            if pos.startswith('ni') or \
                    pos.startswith('na') or \
                    pos.startswith('vii') or \
                    pos.startswith('vai') or \
                    pos.startswith('vti') or \
                    pos.startswith('vta'):
                if 'base_form' not in lex_entry or  lex_entry['base_form'] == '':
                    lex_entry['base_form'] = lex_entry['lex']
                    changed = True

                if 'morphology' not in lex_entry or  lex_entry['morphology'] == '':
                    lex_entry['morphology'] = lex_entry['lex']
                    changed = True

            if changed:
                pos_s.append(pos)
                print(lex_id)
                print('lx:', lex_entry['lex'])
                print('pos:', lex_entry['pos'])
                if 'derivations' in lex_entry:
                    print('deriv:', lex_entry['derivations'])
                print('basef:', lex_entry['base_form'])
                print('morph:', lex_entry['morphology']+'\n')



        save_lex[lex_id] = lex_entry
    print(sorted(set(pos_s)))

    with open(args.lexicon_out,'w') as fout:
        json.dump(save_lex,fout,ensure_ascii=True,sort_keys=True)

main()