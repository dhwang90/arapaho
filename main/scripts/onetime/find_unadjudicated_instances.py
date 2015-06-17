import argparse
import json
from datetime import datetime


__author__ = 'jena'

def ordered(obj):
    if isinstance(obj, dict):
        return sorted((k, ordered(v)) for k, v in obj.items())
    if isinstance(obj, list):
        return sorted(ordered(x) for x in obj)
    else:
        return obj


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('lexicon')
    parser.add_argument('problem_file')
    parser.add_argument('corrected_file')
    args = parser.parse_args()

    with open(args.lexicon) as fin:
        lexicon = json.load(fin)

    lexicon_by_key = {}
    for lexid, lexitem in lexicon.items():
        lex = lexitem['lex']
        pos = "" # lexitem['pos']
        k = (lex,pos)
        if k not in lexicon_by_key:
            lexicon_by_key[k] = []
        lexicon_by_key[k].append(lexitem)



    with open(args.problem_file) as fin:
        entry = json.load(fin)

    i = 0
    t = 0

    lexout = {}

    for entryid, entryitem in entry.items():
        t += 1
        entry_lexid = entryitem['lexid']
        if entry_lexid.startswith('New'):
            lex = entryitem['lex']
            pos = "" # entryitem['pos']
            k = (lex,pos)
            if k not in lexicon_by_key:
                i+= 1

                lexout[entryid] = entryitem
                #print(entry_lexid)
                # print (k, entryitem['pos'])
                # print(lexicon_by_key[k][0]['lex'],lexicon_by_key[k][0]['pos'])
        else:
            if entry_lexid in lexicon:
                #print(entry_lexid)
                entry_time = datetime.strptime(entryitem['date_modified'],'%Y-%m-%d %H:%M:%S')
                lex_time = datetime.strptime(lexicon[entry_lexid]['date_modified'],'%Y-%m-%d %H:%M:%S')

                if entry_time > lex_time:
                    i+= 1
                    
                    if 'senses' in entryitem and 'senses' in lexicon[entry_lexid]:
                        if len(entryitem['senses']) == 1 and len(lexicon[entry_lexid]['senses']) == 1:
                            if 'sources' in lexicon[entry_lexid]['senses'][0] \
                                    and ('sources' not in entryitem['senses'][0] or entryitem['senses'][0]['sources'] == ''):
                                entryitem['senses'][0]['sources'] = lexicon[entry_lexid]['senses'][0]['sources']
                            if 'scientific' in lexicon[entry_lexid]['senses'][0] \
                                    and ('scientific' not in entryitem['senses'][0] or entryitem['senses'][0]['scientific'] == ''):
                                entryitem['senses'][0]['scientific'] = lexicon[entry_lexid]['senses'][0]['scientific']
                            if 'synonym' in lexicon[entry_lexid]['senses'][0] \
                                    and ('synonym' not in entryitem['senses'][0] or entryitem['senses'][0]['synonym'] == ''):
                                entryitem['senses'][0]['synonym'] = lexicon[entry_lexid]['senses'][0]['synonym']

                        else:
                            for sense in entryitem['senses']:
                                for sense_ref in lexicon[entry_lexid]['senses']:
                                    periodless = sense['definition'].strip('.').lower()
                                    if sense_ref['definition'].strip('.').lower() == sense['definition'].strip('.').lower():
                                        #print ('xxx')
                                        if ('sources' not in sense or sense['sources']=="") and ('sources' in sense_ref):
                                            #print('xxx',sense['sources'] , sense_ref['sources'])
                                            sense['sources'] = sense_ref['sources']
                                        if ('scientific' not in sense or sense['scientific']=="") and ('scientific' in sense_ref):
                                            sense['scientific'] = sense_ref['scientific']
                                        if ('synonym' not in sense or sense['synonym']=="") and ('synonym' in sense_ref):
                                            sense['synonym'] = sense_ref['synonym']
                    

                    # print(ordered(entryitem))
                    # print(ordered(lexicon[entry_lexid]),'\n')

                    lexout[entryid] = entryitem

    with open(args.corrected_file,'w') as fout:
        json.dump(lexout,fout,ensure_ascii=True,sort_keys=True)

    print (i,t)

main()