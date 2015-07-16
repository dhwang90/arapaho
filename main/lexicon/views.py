from collections import OrderedDict
import os
import json
from datetime import datetime
from django.shortcuts import render, redirect
from django.conf import settings
from django.template import RequestContext
from django.template.loader import render_to_string
import shutil
from lexicon.mylib import fuzzy_search, parse_entry_form, load_unadjudicated_sessions, make_session_name, \
    make_admin_session_name, unadjudicated_sessions_available, temp_sessions_to_json, save_to_lexicon, \
    system_file_parse, renew_lexicon_stub, starts_with, fuzzy_search_select



# SESSION VARIABLES

SESSION_VARIABLES = ['session_file', 'uas', 'uas_updated', 'open_session',
                     'admin_session_file', 'lexicon', 'last_used_lexid', 'user_permissions']

POS_GROUPS = {'vai':'verb',
              'vti':'verb',
              'vii':'verb',
              'vta':'verb',
              'na':'noun',
              'ni':'noun',
              'ni/vii':'noun'}

# session_file: temp file name where editor's updates to lexicon are saved
#               when the editor chooses to "end session",
#               the contents of this file are output as a single unique file under unadjudicated_sessions/,
#               at this point the session_file is cleared for a new one.
#
# open_session:
#
# uas: unadjudicated sessions
#               when admin chooses to "adjudicate sessions", the files unadjudicated sessions/
#               session_files are collected up as uas
#               adjudicating an instance/lexical item in uas will
#               - output the adjudicated instance/lexical item into the admin_session_temp
#               - +1 on uas_updated
#
# uas_updated: this is a value of number of adjudicated instances/lexical items
#
# admin_session_file: temp file where admin's adjudications are saved
#               when the admin chooses to "end session" (save adjudication),
#               the contents of this file are collected up and reconciled to lexicon
#
# lexicon: contents of settings.LEXICON_DATA_DICT
#          populated at the start of a session (read of file)
#          updated when adjudications are saved (update to variable, accompanied by write to file)
#
# last_used_lexid: last used lexid (regex L[0-9]+)
#          this value is the int version without the initial L
#          generated at lexicon generation
#          updated at lexicon update
#
# user_permissions: list of all the group assignments from system.txt.
# username:


def index_handler(request):
    return render(request, 'index.html')


def main_handler(request):
    if settings.SETTINGS_LOCAL:
        username = 'hwangd'
    else:
        if "REMOTE_USER" in request.META:
            username = request.META["REMOTE_USER"]
        else:
            username = "default_admin"

    if 'username' not in request.session or request.session['username'] != username:
        request.session['username'] = username

    template_values = {'username': username}

    # temporary storage of session filename
    if 'session_file' not in request.session:
        request.session['session_file'] = make_session_name(settings.LEXICON_DATA_SESSIONS_TEMP, username)

    if 'lexicon' not in request.session:
       request.session['lexicon'],request.session['last_used_lexid'] = renew_lexicon_stub()
        # print('LAST NO: ',request.session['last_used_lexid'])

    #print(request.session['lexicon']['L14646'])

    user_permissions = system_file_parse()

    if 'user_permissions' not in request.session:
        request.session['user_permissions'] = user_permissions
        template_values['user_permission'] = user_permissions[username][0]
    else:
        template_values['user_permission'] = request.session['user_permissions'][username][0]

    # temporary storage of session filename
    if template_values['user_permission'] == 'admin' and 'admin_session_file' not in request.session:
        request.session['admin_session_file'] = make_admin_session_name(settings.LEXICON_DATA_SESSIONS_TEMP, username)


    return render(request, 'main.html', template_values)


def clear_temp(request):
    for sv in SESSION_VARIABLES:
        if sv in request.session:
            del request.session[sv]

    return render(request, 'confirmation.html', {'out_message': "Session Variables Cleared"})


def renew_lexicon(request):
    with open(settings.LEXICON_DATA_DICT, 'r') as infile:
        lexicon = json.load(infile)

    klist = []
    for k in lexicon.keys():
        klist.append(int(k.replace('L','')))

    request.session['lexicon'],request.session['last_used_lexid'] = renew_lexicon_stub()

    return render(request, 'confirmation.html', {'out_message': "Lexicon renewed."})


def reload_user(request):
    if settings.SETTINGS_LOCAL:
        username = 'hwangd'
    else:
        if "REMOTE_USER" in request.META:
            username = request.META["REMOTE_USER"]
        else:
            username = "default_admin"

    request.session['username'] = username


    return render(request, 'confirmation.html', {'out_message': "User " + username + " reloaded."})


def utilities(request):
    if request.method == 'GET':
        template_values = {'upload_url': '/upload'}
        return render(request, 'utilities.html', template_values)


def search(request):
    if request.method == 'POST':
        lex = request.POST.get('lex')
        gloss = request.POST.get('gloss')
        pos = request.POST.get('pos')
        base_form = request.POST.get('base_form')
        show_count = request.POST.get('show_count')

        outlist = fuzzy_search(request.session['lexicon'], lex, gloss, pos, base_form, int(show_count))

        context_instance = RequestContext(request)

        if 'editor' in request.session['user_permissions'][request.session['username']]:
            new_form = {'lex': lex, 'gloss': gloss, 'pos': pos, 'base_form': base_form, 'lexid': 'New', 'form': '',
                        'editmode': 'edit', 'user': '', 'curr_user': request.session['username']}
            new_form['form'] = render_to_string('entry_form.html', new_form, context_instance=context_instance)

            for i in range(len(outlist)):
                outlist[i]['editmode'] = 'edit'
                outlist[i]['curr_user'] = request.session['username']
                outlist[i]['form'] = render_to_string('entry_form.html', outlist[i], context_instance=context_instance)
            template_values = {'lex': lex, 'gloss': gloss, 'pos': pos, 'base_form': base_form,
                               'show_count': show_count, 'new_form': new_form, 'outlist': outlist}
        else:
            for i in range(len(outlist)):
                outlist[i]['editmode'] = 'view'
                outlist[i]['form'] = render_to_string('entry_form.html', outlist[i], context_instance=context_instance)
            template_values = {'lex': lex, 'gloss': gloss, 'pos': pos, 'base_form': base_form,
                               'show_count': show_count, 'outlist': outlist}

    else:
        template_values = {'lex': '', 'gloss': '', 'pos': '', 'base_form': '', 'show_count': '10', 'outlist': []}

    if 'open_session' in request.session:
        template_values['open_session'] = request.session['open_session']
    template_values['editmode'] = 'edit'
    template_values['username'] = request.session['username']
    template_values['user_permission'] = request.session['user_permissions'][template_values['username']][0]

    return render(request, 'search.html', template_values)


def view_search(request):
    if request.method == 'POST':
        search_string = request.POST.get('search_string')
        language = request.POST.get('language')
        if language == 'english':
            search_field = 'gloss'
        else:
            search_field = 'lex'

        outdict = {}
        pre_outlist = fuzzy_search_select(request.session['lexicon'], search_string, search_field)
        for item in pre_outlist:
            pos = item['pos'].split('.')[0]
            if pos in POS_GROUPS:
                gpos = POS_GROUPS[pos]
            else:
                gpos = 'other'

            if gpos not in outdict:
                outdict[gpos] = []
            outdict[gpos].append(item)

        for k,outlist in outdict.items():
            for i in range(len(outlist)):
                outlist[i]['form'] = render_to_string('public/view_form.html', outlist[i])

        template_values = {'search_string': search_string, 'language': language, 'outdict': outdict}
    else:
        if 'lexicon' not in request.session:
           request.session['lexicon'],request.session['last_used_lexid'] = renew_lexicon_stub()
        template_values = {'search_string': '', 'language':'english','outdict': {}}

    return render(request, 'public/view_search.html', template_values)


def modify_entry(request, editmode=None):
    # print('editmode', editmode)
    if request.method == 'POST':
        fields = {}
        entry_key = None
        discard = False
        delete = False

        # get as list and make a dict so that we can pass it to parse entry form
        for k in request.POST:

            # #### Handle non data portion of the fields

            # discard changes (just flags an entry to be ignored during adjudication)
            if k == 'discard_changes':
                discard = True
                continue

            # remove lexical item should trigger the lexical item's status to be set to "deleted"
            elif k == 'remove_lexical_item':
                fields['status'] = 'deleted'
                delete = True
                continue

            # entry_id, entry, entry_date
            # entry for lexical entry... in retrospect perhaps it should have been labeled better ah well
            # entry id != lexid. Lexid is the lexical item id, but lexical entry id is the id associated with the
            # changes made by the user. For example a user may have, in the same session, decided to edit a single
            # lexical item twice. Then you have two lexical entries relating to one lexical item.
            # these fields are called during the "user" and entry key parsing just below this line

            elif k in ['entry_id', 'entry_date', 'entry']:
                continue

            # #### GET entry key information

            if k == 'user' and request.POST.get("user"):
                entry_key = [request.POST.get('user'), request.POST.get('entry_date'), request.POST.get('entry_id')]

            # #### Now for parsing ---> REAL <--- data fields:
            items = request.POST.getlist(k)
            if len(items) > 1:
                fields[k] = items[:]
            else:
                fields[k] = items[0]

        # produce json format on the new addition or change
        if fields['lexid'].startswith('New'):
            lexical_item = {}
        else:
            lexical_item = request.session['lexicon'][fields['lexid']]

        lex_item = parse_entry_form(lexical_item, json_format=True, **fields)

        if editmode == 'adjudication':
            if not discard:
                # dump in admin session file (temp loc)
                with open(request.session['admin_session_file'], 'a') as fout:
                    fout.write(lex_item+'\n')
            # else if discard then just don't write to the session file that would be set for save

            # 0 user, entry_date, entry_id
            del request.session['uas'][entry_key[0]][entry_key[1]][entry_key[2]]
            if len(request.session['uas'][entry_key[0]][entry_key[1]]) == 0:
                del request.session['uas'][entry_key[0]][entry_key[1]]
            if len(request.session['uas'][entry_key[0]]) == 0:
                del request.session['uas'][entry_key[0]]


            if 'uas_updated' in request.session:
                request.session['uas_updated'] += 1
            else:
                request.session['uas_updated'] = 1

            return redirect('adjudicate', prev_viewed_user=entry_key[0], prev_viewed_date=entry_key[1])

        elif editmode == 'edit':
            # dump in session file (temp loc)
            with open(request.session['session_file'], 'a') as fout:
                fout.write(lex_item+'\n')

            if 'open_session' not in request.session:
                request.session['open_session'] = []

            if delete:
                request.session['open_session'].append(('Del-'+fields['lexid'], fields['lex'], fields['pos']))
            else:
                request.session['open_session'].append((fields['lexid'], fields['lex'], fields['pos']))

            request.session.modified = True

            return redirect('search')
            #return HttpResponse('<h1>Item saved.</h1><a href="index.html">Main</a>')
        else:
            out_message="uh oh, you should not be seeing this.\nError: modify entry called on neither adjudication or edit modes."
            return render(request, 'confirmation.html', {'out_message': out_message})


    # return render(request, 'validate_entry.html')


def batch_modify(request):
    if request.method == 'POST':
        lex = request.POST.get('lex')
        pos = request.POST.get('pos')
        if "pos_seg" in request.POST:
            pos_seg = True
        else:
            pos_seg = False

        outlist = starts_with(request.session['lexicon'], lex, pos, pos_seg)
        template_values = {'lex': lex, 'pos': pos, 'pos_seg': pos_seg, 'outlist': outlist}
    else:
        template_values = {'lex': '', 'pos': '', 'pos_seg': True, 'outlist': []}
    return render(request, 'batch_modify.html', template_values)
    # return render(request, 'confirmation.html', {'out_message': "you clicked on batch modify"})


def batch_entry(request):
    # note that this parallels end_session()

    batch_fields = ['morphology', 'base_form', 'semantic_domain','status']
    entries = {}
    for k in request.POST:
        if k == 'csrfmiddlewaretoken': continue

        lid, val = k.split('-')
        if lid not in entries:
            entries[lid] = {}
        entries[lid][val] = request.POST.get(k)

    json_out = {}
    today_uniq = datetime.today().strftime(settings.FORMAT_SESSIONS_DATE)  # today's date (unique identifier)

    for lid, val in entries.items():
        lexical_item = request.session['lexicon'][lid]
        lexical_item['lexid'] = lid  # save_to_lexicon() needs this
        has_changes = False

        for b in batch_fields:
            if b not in val: continue
            if (val[b].strip() and b not in lexical_item) or \
                    (b in lexical_item and val[b].strip() != lexical_item[b].strip()):
                lexical_item[b] = val[b]
                has_changes = True
        if has_changes:
            json_out[lid] = lexical_item


    request.session['lexicon'], request.session['last_used_lexid'] = renew_lexicon_stub()
    save_to_lexicon(json_out, request.session['lexicon'], request.session['last_used_lexid'])
    request.session.modified = True

    shutil.move(settings.LEXICON_DATA_DICT,
                settings.LEXICON_DATA_DICT_BACKUP.replace('.json', '-'+ today_uniq + '.json'))

    with open(settings.LEXICON_DATA_DICT, 'w') as fout:
        json.dump(request.session['lexicon'], fout, ensure_ascii=True)

    return render(request, 'confirmation.html', {'out_message': "Your changes have been saved to the lexicon"})


def adjudicate(request, prev_viewed_user=None, prev_viewed_date=None, manual_reload="False"):
    # prev viewed user = username of the previously viewed entry,
    # prev viewed date = date at which the previously viewed entry was submitted for adjudication

    # print('IN ADJUDICATE', prev_viewed_user, prev_viewed_date)

    if request.session['user_permissions'][request.session['username']][0] != "admin":
        return render(request, 'confirmation.html', {'out_message': "Sorry, only an admin can access this page."})
    else:
        # temp ua sessions saves the current unadjudicated sessions to pass to templates
        # this is a little clunky and probably expensive but not sure how else to handle it more smoothly
        temp_ua_sessions = {}

        # if unadjudicated sessions are available
        uas_avail = unadjudicated_sessions_available()
        if uas_avail or 'uas' in request.session:

            # if there are no unadjudicated sessions currently being adjudicated, then create new
            # if there unadjudication sessions are empty, then add more
            # if manual reload, then add to the current session

            if 'uas' not in request.session or len(request.session['uas']) == 0 or manual_reload=="True":
                unadjudicated_sessions = load_unadjudicated_sessions()

                if 'uas' not in request.session:
                    request.session['uas_updated'] = 0
                    request.session['uas'] = unadjudicated_sessions
                elif len(request.session['uas']) == 0:
                    request.session['uas'] = unadjudicated_sessions
                else:
                    for u in unadjudicated_sessions:
                        if u not in request.session['uas']:
                            request.session['uas'][u] = unadjudicated_sessions[u]
                        else:
                            request.session['uas'][u].update(unadjudicated_sessions[u])
                        request.session.modified = True


            # # if there are unadjudicated sessions still being looked at then add to it
            # elif len(unadjudicated_sessions) > 0:
            #     for u in unadjudicated_sessions:
            #         if u not in request.session['uas']:
            #             request.session['uas'][u] = unadjudicated_sessions[u]
            #         else:
            #             request.session['uas'][u].update(unadjudicated_sessions[u])
            #         request.session.modified = True

            context_instance = RequestContext(request)

            for entry_user, u_sessions in request.session['uas'].items():
                if entry_user not in temp_ua_sessions:
                    temp_ua_sessions[entry_user] = {}

                for entry_date, u_session in u_sessions.items():

                    session_entries = OrderedDict()
                    for entry_id, entry in sorted(u_session.items()):
                        pass_entry = entry.copy()

                        # entry identifier key
                        pass_entry['user'] = entry_user
                        pass_entry['entry_date'] = entry_date
                        pass_entry['entry_id'] = entry_id

                        # editmode modifications just for the entry_form.html
                        pass_entry['editmode'] = 'adjudication'

                        # lexid modifications strictly for unique entry numbering purposes
                        # see admin statements in entry_form.html
                        pass_entry['lexid_original'] = entry['lexid']

                        # there can be multiple of same lexids and so we need the entry_id for identification
                        pass_entry['lexid'] = entry['lexid'] + entry_date + '-' + entry_id
                        pass_entry['entry'] = entry

                        entry_form = render_to_string('entry_form.html', pass_entry, context_instance=context_instance)
                        session_entries[entry_id] = {"form": entry_form, "entry": entry, "entry_id": entry_id}

                    if entry_date not in temp_ua_sessions[entry_user]:
                        temp_ua_sessions[entry_user][entry_date] = {}

                    if 'forms' not in temp_ua_sessions[entry_user][entry_date]:
                        temp_ua_sessions[entry_user][entry_date]['forms'] = []

                    for sid, session_entry in session_entries.items():
                        # if prev_viewed_key and prev_viewed_key == entry_user+'_'+entry_date:
                        session_form = render_to_string('adjudicate_sessions.html', session_entry)
                        temp_ua_sessions[entry_user][entry_date]['forms'].append(session_form)

                    if prev_viewed_user and prev_viewed_user == entry_user and prev_viewed_date == entry_date:
                        temp_ua_sessions[entry_user][entry_date]['prev_viewed'] = 'T'

        temp_uas_cnt = request.session['uas_updated'] if 'uas_updated' in request.session else 0
        template_values = {'username': request.session['username'], 'unadjudicated_sessions': temp_ua_sessions,
                           'uas_updated_current_count': str(temp_uas_cnt), 'editmode':'adjudication'}

        return render(request, 'adjudicate.html', template_values)


def end_session(request, editmode):
    if 'session_file' not in request.session:
        if 'open_session' in request.session:
            del request.session['open_session']

        out_message = "You do not currently have an open session"
        return render(request, 'confirmation.html', {'out_message': out_message})
    else:
        # package up everything in file, create a json file
        if editmode == 'adjudication':
            session_file_name = 'admin_session_file'
        else:
            session_file_name = 'session_file'

        temp_session_filename = request.session[session_file_name]

        if not os.path.exists(temp_session_filename):
            if 'open_session' in request.session:
                del request.session['open_session']

            if request.session['uas_updated'] > 0:
                request.session['uas_updated'] = 0

            out_message = 'You do not have any new edits or updates to lexical entries.'
            return render(request, 'confirmation.html', {'out_message': out_message})

        temp_session_filename_base = os.path.basename(temp_session_filename)

        json_out = temp_sessions_to_json(temp_session_filename)     #entries in json format
        today_uniq = datetime.today().strftime(settings.FORMAT_SESSIONS_DATE)  # today's date (unique identifier)


        if editmode == 'adjudication' or ('admin' in request.session['user_permissions'][request.session['username']]
                                          and settings.ADMIN_BYPASS):

            request.session['lexicon'],request.session['last_used_lexid'] = renew_lexicon_stub()
            save_to_lexicon(json_out, request.session['lexicon'], request.session['last_used_lexid'])
            request.session.modified = True

            # print(json_out, request.session['lexicon']['L14217'])

            shutil.move(settings.LEXICON_DATA_DICT,
                        settings.LEXICON_DATA_DICT_BACKUP.replace('.json', '-'+ today_uniq + '.json'))

            with open(settings.LEXICON_DATA_DICT, 'w') as fout:
                json.dump(request.session['lexicon'], fout, ensure_ascii=True)

            if editmode == 'adjudication':
                del request.session['uas_updated']
                out_message = 'Your adjudications have been saved to the lexicon.'
            else:
                del request.session['open_session']
                out_message = 'Your entries have been saved to the lexicon.'

        else:
            # editmode == edit
            # save to settings.LEXICON_DATA_SESSIONS under the same filename_base (use dump)
            fname = temp_session_filename_base.split('-')[0] + '-' + today_uniq + '.json'
            with open(os.path.join(settings.LEXICON_DATA_SESSIONS, fname), 'w') as fout:
                fout.write(json.dumps(json_out, ensure_ascii=True, sort_keys=True))

            del request.session['open_session']

            out_message = 'Your entries have been saved for adjudication.'

        # delete session_file
        os.remove(temp_session_filename)
        del request.session[session_file_name]

        return render(request, 'confirmation.html', {'out_message': out_message})


def temp_allolex(request):
    #return render(request, 'confirmation.html', {'out_message': 'main'})
    return render(request, 'temp/temp_allolex.html')


def temp_allolex_pos(request):
    return render(request, 'confirmation.html', {'out_message': 'pos'})
    #return render(request, 'temp/temp_allolex_pos.html')


def temp_allolex_gloss(request):
    return render(request, 'confirmation.html', {'out_message': 'gloss'})
    #return render(request, 'temp/temp_allolex_gloss.html')


def temp_allolex_new(request):
    return render(request, 'confirmation.html', {'out_message': 'new'})
    #return render(request, 'temp/temp_allolex_new.html')

# def logout(request):
#     return HttpResponse(content, status=401)


