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
    return lexicon

parser = argparse.ArgumentParser()
parser.add_argument('filename')
args = parser.parse_args()

lexicon = read_xml(args.filename)

with open(args.filename.replace('.xml', '.json'), 'w') as outfile:
    # json.dump(lexicon, outfile, sort_keys=True, indent=4, ensure_ascii=False)
    json.dump(lexicon, outfile, sort_keys=True, ensure_ascii=False)

# with open(args.filename + '.json', 'r') as infile:
#     lexicon = json.load(infile)