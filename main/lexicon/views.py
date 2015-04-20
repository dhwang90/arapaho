from collections import OrderedDict
import os
import uuid
import json
from django.shortcuts import render
from django.conf import settings
from django.template import RequestContext
from django.template.loader import render_to_string
from lexicon.mylib import fuzzy_search, parse_entry_form
from django.http import HttpResponse



USERNAME = 'hwangd'
PERMISSIONS = {'admin':('admin','editor','viewer'), 'editor':('editor','viewer'), 'viewer':('viewer')}


def main_handler(request):
    # if "REMOTE_USER" in request.META:
    #     username = request.META("REMOTE USER")
    # else:
    #     username = "default_admin"
    #

    template_values = {'username': USERNAME}

    # temporary storage of session filename
    if 'session_file' not in request.session:
        request.session['session_file'] = os.path.join(settings.LEXICON_DATA_SESSIONS_TEMP, USERNAME + '-' + str(uuid.uuid1()))  #for session file naming purposes


    if 'lexicon' not in request.session:
        with open(os.path.join(settings.LEXICON_DATA, 'arapaho_lexicon.json'), 'r') as infile:
            lexicon = json.load(infile)
        request.session['lexicon'] = lexicon

    if 'user_permission' not in request.session:
        user_permission = OrderedDict()
        with open(settings.GROUP_PERMISSION_FILE_PATH, 'r') as infile:
            for line in infile:
                permission, users = line.strip().split(':')
                us = users.split(',')
                for u in us:
                    user_permission[u] = PERMISSIONS[permission]

        request.session['user_permission'] = user_permission
        template_values['user_permission'] = user_permission[USERNAME][0]
    else:
        template_values['user_permission'] = request.session['user_permission'][USERNAME][0]


    return render(request, 'index.html', template_values)


def end_session(request):
    if 'session_file' not in request.session:
        return HttpResponse('<h1>You do not currently have an open session</h1><a href="index.html">Main</a>')
    else:
        # package up everything in file, create a real unadjudicated_session
        temp_session_filename = request.session['session_file']

        if not os.path.exists(temp_session_filename):
            return HttpResponse('<h1>You do not have any new edits or updates to the lexical dictionary</h1><a href="index.html">Main</a>')

        temp_session_filename_base = os.path.basename(temp_session_filename)

        json_line = "{"
        with open(temp_session_filename,'r') as fin:
            for i, line in enumerate(fin):
                json_line += '\n"'+str(i)+'":' +line.strip() + ','
            json_line = json_line.strip(',') + "\n}"

        print(json_line)
        json_out = json.loads(json_line)

        # save to settings.LEXICON_DATA_SESSIONS under the same filename_base (use dump)
        with open(os.path.join(settings.LEXICON_DATA_SESSIONS,temp_session_filename_base+'.json'),'w') as fout:
            fout.write(json.dumps(json_out,ensure_ascii=True,sort_keys=True))

        # delete tempfile
        #os.remove(temp_session_filename)

        # delete session_file
        #del request.session['session_file']
        return HttpResponse('<h1>Your session has been saved.</h1><a href="index.html">Main</a>')



def clear_temp(request):
    if 'lexicon' in request.session:
        del request.session['lexicon']
        del request.session['user_permission']
        del request.session['session_file']

    return HttpResponse('<h1>Cleared</h1><a href="index.html">Main</a>')

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

        editor = True
        if editor:
            new_form = {'lex': lex, 'gloss': gloss, 'pos': pos, 'base_form': base_form, 'lexid': 'New', 'form': ''}
            new_form['usertype'] = 'editor'
            new_form['form'] = render_to_string('entry_form.html', new_form, context_instance=context_instance)

            for i in range(len(outlist)):
                outlist[i]['usertype'] = 'editor'
                outlist[i]['form'] = render_to_string('entry_form.html', outlist[i], context_instance=context_instance)
            template_values = {'lex': lex, 'gloss': gloss, 'pos': pos, 'base_form': base_form,
                               'show_count': show_count, 'new_form': new_form, 'outlist': outlist}
        else:
            for i in range(len(outlist)):
                outlist[i]['usertype'] = 'normal'
                outlist[i]['form'] = render_to_string('entry_form.html', outlist[i], context_instance=context_instance)
            template_values = {'lex': lex, 'gloss': gloss, 'pos': pos, 'base_form': base_form,
                               'show_count': show_count, 'outlist': outlist}

    else:
        template_values = {'lex': '', 'gloss': '', 'pos': '', 'base_form': '', 'show_count': '10', 'outlist': []}

    return render(request, 'search.html', template_values)


def modify_entry(request):
    if request.method == 'POST':
        fields = {}
        for k in request.POST:
            items = request.POST.getlist(k)
            if len(items) > 1:
                fields[k] = items[:]
            else:
                fields[k] = items[0]

        # produce json format on the new addition or change
        lex_item = parse_entry_form(json_format = True, **fields)
        print(lex_item)

        # dump in file

        print(request.session['session_file'])
        with open(request.session['session_file'], 'a') as fout:
            fout.write(lex_item+'\n')

    return HttpResponse('<h1>Item saved.</h1><a href="main.html">Main</a>')

    #return render(request, 'validate_entry.html')

def adjudicate(request):

    return render(request, 'adjudicate.html')