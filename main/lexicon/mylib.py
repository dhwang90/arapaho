# -*- coding: utf-8 -*-

import collections
from datetime import datetime
import difflib
import glob
import json
import os
import shutil
import uuid
from django.conf import settings


PERMISSIONS = {'admin': ('admin', 'editor', 'viewer'),
               'editor': ('editor', 'viewer'), 'viewer': ('viewer')}


# ### MAIN FUNCTIONS ####


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
        if 'status' in lexicon[k] and lexicon[k]['status'] == 'deleted':
            continue

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
            lexicon[k]['lexid'] = k   # APPEND IN LEX ID for ease of search
            templist.append((score, fix_date(lexicon[k])))
            number += 1
    templist.sort(key=lambda x: x[0], reverse=True)
    for lexical_item in templist:
        outlist.append(lexical_item[1])
    return outlist[:show_count]


def fuzzy_search_select(lexicon, search_string, search_field):
    outlist = []
    templist = []
    number = 0

    for k in lexicon:
        if 'status' in lexicon[k] and lexicon[k]['status'] == 'deleted':
            continue

        try:
            item_lex = lexicon[k][search_field]
            if search_field == 'gloss':
                item_lex = item_lex.split('(')[0]
        except KeyError:
            item_lex = ''

        try:
            pos = lexicon[k]['pos']
        except KeyError:
            pos = ''


        if not item_lex or \
            pos in ['ENGL','label','persname','placename'] or \
            pos.startswith('x') or \
            '.pl' in pos or '.obv' in pos:
            continue


        threshold = 1.1
        score = scorer(search_string, item_lex)
        if search_string in item_lex:
            score += 0.2

        #print(score,threshold)

        if score > threshold:
            lexicon[k]['lexid'] = k   # APPEND IN LEX ID for ease of search
            lexicon[k]['score'] = str(score)
            templist.append((score, fix_date(lexicon[k])))
            number += 1
    templist.sort(key=lambda x: x[0], reverse=True)
    for lexical_item in templist:
        outlist.append(lexical_item[1])
    return outlist


def starts_with(lexicon, lex, pos, pos_seg):
    outlist = []
    templist = []
    for k in lexicon:
        if ('status' in lexicon[k] and lexicon[k]['status'] == 'deleted') or \
            (pos_seg and len(lexicon[k]['pos'].split('.')) > 1):
            continue

        if (lex and pos and lexicon[k]['lex'].startswith(lex) and lexicon[k]['pos'].startswith(pos)) or \
                (lex and not pos and lexicon[k]['lex'].startswith(lex)) or \
                (pos and not lex and lexicon[k]['pos'].startswith(pos)):
            templist.append((lexicon[k]['lex'], fix_date(lexicon[k])))
            lexicon[k]['lexid'] = k   # APPEND IN LEX ID for ease of search

    templist.sort(key=lambda x: x[0], reverse=True)

    for lexical_item in templist:
        outlist.append(lexical_item[1])

    return outlist


def parse_entry_form(lexical_item, json_format, **kwargs):
    lexitem = {}
    senses = []
    derivations = {}

    date_stamp = datetime.today().strftime(settings.FORMAT_JSON_SAVE_DATE)

    # senses, derivations, and date modified are fields that don't appear in those particular words
    # as names to fields in the entry form. But these are accounted for.
    labels_visited = ['senses', 'derivations', 'date_modified', 'verified'] # verified must be removed eventually

    for k, v in kwargs.iteritems():
        labels_visited.append(k)
        if k in ['variant_forms','allolexemes']:
            lexitem[k] = is_list(kwargs.get(k, None))

        elif k == 'deriv_type':
            deriv_type = is_list(kwargs.get(k, None))

            if len(deriv_type) > 0:
                deriv_value = is_list(kwargs.get('deriv_value', None))
                for i, d in enumerate(deriv_type):
                    derivations[d] = deriv_value[i]

        elif k == 'definition':
            # senses
            defs = is_list(kwargs.get('definition', None))

            if len(defs) > 0:

                temp = {}
                for val in ['usage', 'scientific', 'synonym', 'note', 'sources', 'example']:
                    temp[val] = is_list(kwargs.get(val, None))

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

        elif k in ['usage', 'scientific', 'synonym', 'note', 'sources', 'csrfmiddlewaretoken', 'deriv_value','example']:
            continue

        else:
            # lexid, lex, base_form, gloss, pos, language, morphology, cultural, literal, etymology
            # semantic_domain

            # NEW entry
            if k == 'lexid' and v == 'New':
                lexitem[k] = 'New-'+str(uuid.uuid1())
                lexitem['date_added'] = date_stamp

            # NEW adjudication
            elif k == 'lexid' and v.startswith('New'):
                lexitem[k] = v
                lexitem['date_added'] = date_stamp

            # UPDATE entry
            else:
                lexitem[k] = v


    lexitem['senses'] = senses
    lexitem['derivations'] = derivations
    lexitem['date_modified'] = date_stamp

    for lex_field, field_content in lexical_item.items():
        if lex_field not in labels_visited:
            lexitem[lex_field] = field_content

    if json_format:
        return json.dumps(lexitem, sort_keys=True, ensure_ascii=True)
    else:
        return lexitem


def load_unadjudicated_sessions():
    u_sessions = {}

    for f in glob.glob(os.path.join(settings.LEXICON_DATA_SESSIONS, '*.json')):
        if '-under-adjudication' in f:
            continue

        fname = os.path.basename(f).split('.')[0]
        fn = fname.split('-')
        user = fn[0]
        date = '-'.join(fn[1:]) #datetime.strptime('-'.join(fn[1:]),settings.FORMAT_SESSIONS_DATE)

        if user not in u_sessions:
            u_sessions[user] = {}

        with open(f) as fin:
            u_sessions[user][date] = json.load(fin)

        shutil.move(f, f.replace(".json", "-under-adjudication.json"))

    return u_sessions


def get_unadjudicated_sessions(adjudicator):
    # not yet adjudicated sessions
    available_sessions = {}

    for f in glob.glob(os.path.join(settings.LEXICON_DATA_SESSIONS, '*.json')):
        if '-under-adjudication' in f:
            continue

        fname, annotator, date = parse_annotation_filename(f)

        if annotator not in available_sessions:
            available_sessions[annotator] = {}

        available_sessions[annotator][date] = {}
        available_sessions[annotator][date][fname] = 'N' # new

    # adjudication in progress

    for f in glob.glob(os.path.join(settings.LEXICON_DATA_ADJUDICATION+adjudicator+'/', '*.json')):
        if '-committed' in f or '-adjudicated' in f or '-discarded' in f:
            continue

        fname, annotator, date = parse_annotation_filename(f)

        if annotator not in available_sessions:
            available_sessions[annotator] = {}

        available_sessions[annotator][date] = {}
        available_sessions[annotator][date][fname] = 'P'  #in progress

    return available_sessions


def open_unadjudicated_session(filename, username, status):
    u_sessions = []

    fname, annotator, date = parse_annotation_filename(filename)
    adjudicator_dir = settings.LEXICON_DATA_ADJUDICATION+'/'+username+'/'
    adjudication_filename = os.path.join(adjudicator_dir,filename+'.json')

    if status == 'N':
        # UNADJUDICATED FILE
        unadjudicated_filename = os.path.join(settings.LEXICON_DATA_SESSIONS,filename+'.json')
        with open(unadjudicated_filename) as fin:
            u_sessions.append((annotator, date, json.load(fin)))

        # ADJUDICATION FILE
        if not os.path.exists(adjudicator_dir):
            os.makedirs(adjudicator_dir)

        # COPY UNADJUICATED TO ADJUDICATION; AND RENAME ORIGINAL
        shutil.copy(unadjudicated_filename, adjudication_filename)
        shutil.move(unadjudicated_filename, unadjudicated_filename.replace(".json", "-under-adjudication.json"))
    else: # if P (in progress)
        with open(adjudication_filename) as fin:
            u_sessions.append((annotator, date, json.load(fin)))

    return u_sessions

def unadjudicated_sessions_available():
    for f in glob.glob(os.path.join(settings.LEXICON_DATA_SESSIONS, '*.json')):
        if '-under-adjudication' in f:
            continue
        return True
    return False


def get_lexids(jsonfile):
    lexids = []
    for entryid,entry in jsonfile.items():
        lexids.append(entry['lexid'])
    return lexids


def system_file_parse():
    user_permission = collections.OrderedDict()
    with open(settings.SYSTEM_FILE_PATH, 'r') as infile:
        for line in infile:
            # handle comments and empty lines
            if line.startswith("#") or line.strip() == '':
                continue
            l = line.split('#')[0]

            seg = l.strip().split(':')

            if seg[0] == 'group':
                permission = seg[1]
                users = seg[2]
                us = users.split(',')
                for u in us:
                    user_permission[u] = PERMISSIONS[permission]

    return user_permission


def save_to_lexicon(updates_json, lexicon, last_used_lexid):
    # sample reminder: L14217
    for _, update_lexitem in updates_json.items():
        lexid = update_lexitem['lexid']
        del update_lexitem['lexid']
        del update_lexitem['session_filename'] #added in at adjudicate_file() for the purposes of template

        if lexid.startswith('New'):
            last_used_lexid += 1
            lexid = 'L'+str(last_used_lexid)

        lexicon[lexid] = update_lexitem


# ### HELPERS ####

def is_list(vf):
    if vf:
        if isinstance(vf, list):
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
    return datetime.strptime(d, settings.FORMAT_JSON_SAVE_DATE)


def make_session_name(dir_, user):
    return os.path.join(dir_, user + '-' + str(uuid.uuid1()))


def make_admin_session_name(dir_, user):
    return os.path.join(dir_, 'admin-' + user + '-' + str(uuid.uuid1()))


def temp_sessions_to_json(temp_session_filename):
    json_line = "{"
    with open(temp_session_filename, 'r') as fin:
        for i, line in enumerate(fin):
            json_line += '\n"'+str(i)+'":' + line.strip() + ','
        json_line = json_line.strip(',') + "\n}"

    # print(json_line)
    return json.loads(json_line)


def renew_lexicon_stub():
    with open(settings.LEXICON_DATA_DICT, 'r') as infile:
        lexicon = json.load(infile)

    klist = []
    for k in lexicon.keys():
        klist.append(int(k.replace('L','')))

    return lexicon, sorted(klist)[-1]


def ordered(obj):
    if isinstance(obj, dict):
        return sorted((k, ordered(v)) for k, v in obj.items())
    if isinstance(obj, list):
        return sorted(ordered(x) for x in obj)
    else:
        return obj


def parse_annotation_filename(filename):
    fbasename = os.path.basename(filename).split('.')[0]
    fn = fbasename.split('-')
    return fbasename, fn[0], '-'.join(fn[1:])
