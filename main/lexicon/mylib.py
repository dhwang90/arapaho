# -*- coding: utf-8 -*-
from collections import OrderedDict

import difflib
import json
import uuid
from datetime import datetime


def scorer(word, criteria):
    word = word.lower()
    score = 0.0

    def internal(crit):
        internal_score = 0.0
        crit = crit.lower()
        if word == crit:
            internal_score += 2
        if word.startswith(crit):
            internal_score += 0.8
        elif crit.startswith(word):
            internal_score += 0.8
        if word in crit:
            internal_score += 0.8
        elif crit in word:
            internal_score += 0.8
        internal_score += difflib.SequenceMatcher(None, crit, word).ratio()

        return internal_score

    if type(criteria) is list:
        for c in criteria:
            score += internal(c)
    else:
        score += internal(criteria)

    return score


def fuzzy_search(lexicon, lex, gloss, pos, base_form, show_count):
    outlist = []
    templist = []
    number = 0
    for k in lexicon:
        try:
            item_lex = lexicon[k]['lex']
        except KeyError:
            item_lex = ''
        try:
            item_gloss = lexicon[k]['gloss']
        except KeyError:
            item_gloss = ''
        try:
            item_pos = lexicon[k]['pos']
        except KeyError:
            item_pos = ''
        try:
            item_base_form = lexicon[k]['base_form']
        except KeyError:
            item_base_form = ''
        threshold = 0.0
        score = 0.0

        if lex:
            threshold += 0.8
            score += scorer(lex, item_lex)
        if gloss:
            threshold += 0.8
            score += scorer(gloss, item_gloss)
        if pos:
            threshold += 0.8
            score += scorer(pos, item_pos)
        if base_form:
            threshold += 0.8
            score += scorer(base_form, item_base_form)
        if score > threshold:
            lexicon[k]['lexid'] = k
            templist.append((score, fix_date(lexicon[k])))
            number += 1
    templist.sort(key=lambda x: x[0], reverse=True)
    for lexical_item in templist:
        outlist.append(lexical_item[1])
    return outlist[:show_count]


def parse_entry_form(json_format, **kwargs):
    lexitem = {}
    senses = []
    derivations = {}

    for k,v in kwargs.iteritems():
        if k  == 'variant_forms':
            lexitem[k] = is_list(kwargs.get(k, None))

        elif k == 'deriv_type':
            print (k,v)
            deriv_type = is_list(kwargs.get(k, None))

            if len(deriv_type) > 0:
                deriv_value = is_list(kwargs.get('deriv_value', None))
                for i,d in enumerate(deriv_type):
                    derivations[d] = deriv_value[i]

        elif k == 'definition':
            # senses
            defs = is_list(kwargs.get('definition', None))

            if len(defs) > 0:

                temp = {}
                for val in ['usage','scientific','synonym','note','sources']:
                    temp[val] = is_list(kwargs.get(val,None))

                # usage       = test_if_list(kwargs.get('usage',None))
                # scientific  = test_if_list(kwargs.get('scientific',None))
                # synonym     = test_if_list(kwargs.get('synonym',None))
                # note        = test_if_list(kwargs.get('note',None))
                # sources     = test_if_list(kwargs.get('sources',None))

                for i, d in enumerate(defs):
                    sense = {'definition': defs[i]}
                    for tk, tv in temp.items():
                        if len(tv) > i:
                            sense[tk] = tv[i]
                        else:
                            sense[tk] = ''
                    senses.append(sense)

        elif k in ['usage','scientific','synonym','note','sources','csrfmiddlewaretoken','deriv_value']:
            continue

        else:
            # lexid, lex, base_form, gloss, pos, language, morphology, cultural, literal, etymology
            # semantic_domain

            if k == 'lexid' and v == 'New':
                lexitem[k] = 'New-'+str(uuid.uuid1())
            else:
                lexitem[k] = v

    lexitem['senses'] = senses
    lexitem['derivations'] = derivations
    lexitem['date_modified'] = datetime.today().strftime('%Y-%m-%d %H:%M:%S')

    if json_format:
        return json.dumps(lexitem, sort_keys=True, ensure_ascii=True)
    else:
        return lexitem


def is_list(vf):
    if vf:
        if isinstance(vf,list):
            return vf
        else:
            return [vf]
    else:
        return []


def fix_date(lexical_item):
    lexical_item['date_added'] = parse_date(lexical_item['date_added'])
    lexical_item['date_modified'] = parse_date(lexical_item['date_modified'])
    return lexical_item


def parse_date(d):
    # YYYY-MM-dd 00:00:00
    return datetime.strptime(d, '%Y-%m-%d %H:%M:%S')
