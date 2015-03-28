# -*- coding: utf-8 -*-

import difflib
import xml.etree.ElementTree as etree
from datetime import datetime


class SearchOut():
    num = 0
    lex = ''
    gloss = ''
    pos = ''
    base_form = ''
    key = ''


def scorer(word, criteria):
    word = word.lower()
    score = 0.0

    def internal(crit):
        internal_score = 0.0
        crit = crit.lower()
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
            temp = SearchOut()
            temp.num = number
            temp.lex = item_lex
            temp.gloss = item_gloss
            temp.pos = item_pos
            temp.base_form = item_base_form
            temp.lexid = k
            templist.append((score, temp))
            number += 1
    templist.sort(key=lambda x: x[0], reverse=True)
    for item in templist:
        outlist.append(item[1])
    return outlist[:show_count]


