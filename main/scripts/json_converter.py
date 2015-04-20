import json
import argparse
import xml.etree.ElementTree as etree
from datetime import datetime


def read_xml(filename):
    utf8_parser = etree.XMLParser(encoding='utf-8')
    tree = etree.parse(filename, parser=utf8_parser)
    root = tree.getroot()

    lextag_map = {'mn': 'base_form', 'all': 'variant_form', 'ps': 'pos', 'lx': 'lex', 'ge': 'gloss',
                  'mr': 'morphology', 'lt': 'literal', 'et': 'etymology'}
    sensetag_map = {'de': 'definition', 'ue': 'usage', 'obv.sg': 'obvsg', 'obv.pl': 'obvpl', 'sc': 'scientific',
                    'sy': 'synonym', 'nt': 'note', 'pl': 'pl', 'obv': 'obv', 'loc': 'loc', 'voc': 'voc', 's3': 's3',
                    'poss3': 'poss3', 'so': 'sources'}

    i = 0
    lexicon = {}
    for lexitem in root:
        lexical_item = {}

        lang = lexitem.get('language').capitalize()
        if lang == 'English' or lang == 'Arapaho':
            lexical_item['language'] = lang
        else:
            lexical_item['language'] = 'Other'
        lexid = lexitem.get('lexid', '-1')

        if lexitem.get('date') != '':
            lexical_item['date_added'] = str(datetime.strptime(lexitem.get('date'), '%d/%b/%Y'))
            lexical_item['date_modified'] = str(datetime.strptime(lexitem.get('date'), '%d/%b/%Y'))
        else:
            if lexitem.get('source') == "03/Nov/2014":
                lexical_item['date_added'] = str(datetime.strptime(lexitem.get('source'), '%d/%b/%Y'))
                lexical_item['date_modified'] = str(datetime.strptime(lexitem.get('source'), '%d/%b/%Y'))
            else:
                lexical_item['date_added'] = str(datetime.strptime('07/Oct/2014', '%d/%b/%Y'))
                lexical_item['date_modified'] = str(datetime.strptime('07/Oct/2014', '%d/%b/%Y'))


        lexical_item['verified'] = True

        for item in lexitem:
            if item.tag == 'senses':
                lexical_item['senses'] = []
                for t in item:
                    tempdict = {}
                    for s in t:
                        if s.text and s.tag in sensetag_map:
                            tempdict[sensetag_map[s.tag]] = s.text
                    lexical_item['senses'].append(tempdict)
            elif item.text:
                if item.tag == 'all':
                    variant_forms = item.text.split(';')
                    lexical_item['variant_forms'] = []
                    for a in variant_forms:
                        lexical_item['variant_forms'].append(a.strip())
                # elif item.tag == 'ps':
                #     lexical_item['pos'] = []
                elif item.tag in lextag_map:
                    lexical_item[lextag_map[item.tag]] = item.text

                if item.tag == 'ps' and item.text.startswith('x'):
                    lexical_item['toolbox_show'] = False

            else:
                # hide x pos from toolbox
                if item.tag == 'ps':
                    lexical_item['verified'] = False
        if lexid in lexicon:
            while str(i).zfill(4) in lexicon:
                i += 1
            lexicon[str(i).zfill(4)] = lexical_item
        else:
            lexicon[lexid] = lexical_item

        # if lexid in lexicon:
        #     while str(i).zfill(4) in lexicon:
        #         i += 1
        #     lexical_item['lexid'] = str(i).zfill(4)
        #     lexicon[str(i).zfill(4)] = lexical_item
        # else:
        #     lexical_item['lexid'] = lexid
        #     lexicon[lexid] = lexical_item


    return lexicon


def edit_tags(lexicon):

    tags_to_move = ['obv','obv.sg','obv.pl','pl','obv', 'loc', 'voc', 's3', 'poss3']
    #tags_to_add = ['semantic_domain'] #sd ... json will rip it out anyway... but this needs to go into guidelines

    for lid, lex_item in lexicon.items():
        if 'senses' not in lex_item: continue
        derivs = {}
        for sense in lex_item['senses']:
            for stag, sdata in sense.items():
                #print(lid, stag,sdata)
                if stag not in tags_to_move or sdata == '': continue

                if stag == 'obv.sg':
                    stag_actual = 'obv'
                else:
                    stag_actual = stag

                if stag_actual not in derivs:
                    derivs[stag_actual] = sdata
                else:
                    print(lid,stag, sense)
            for remove_tag in tags_to_move:
                if remove_tag in sense:
                    del sense[remove_tag]


        lex_item['derivations'] = derivs

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('filename')
    args = parser.parse_args()

    print('reading')
    lexicon = read_xml(args.filename)

    print('editing')
    edit_tags(lexicon)

    print('converting')
    with open(args.filename.replace('.xml','.json'), 'w') as outfile:
        # json.dump(lexicon, outfile, sort_keys=True, indent=4, ensure_ascii=False)
        json.dump(lexicon, outfile, sort_keys=True, ensure_ascii=True)

    # with open(args.filename + '.json', 'r') as infile:
    #     lexicon = json.load(infile)

main()