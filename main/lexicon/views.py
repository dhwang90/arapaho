import os
from json import load as json_load
from django.shortcuts import render_to_response, render
from django.conf import settings
from lexicon.mylib import fuzzy_search
#from django.template import RequestContext
#from django.http import HttpResponseRedirect, HttpResponse


with open(os.path.join(settings.ROOT_PATH, 'lexicon_data/arapaho_lexicon.json'), 'r') as infile:
    lexicon = json_load(infile)


def main_handler(request):
    if "REMOTE_USER" in request.META:
        username = request.META("REMOTE USER")
    else:
        username = "default_admin"

    template_values = {'username': username}
    return render(request, 'index.html', template_values)


def search(request):
    if request.method == 'POST':
        lex = request.POST.get('lex')
        gloss = request.POST.get('gloss')
        pos = request.POST.get('pos')
        base_form = request.POST.get('base_form')
        show_count = request.POST.get('show_count')

        outlist = fuzzy_search(lexicon, lex, gloss, pos, base_form, int(show_count))
        template_values = {'lex': lex, 'gloss': gloss, 'pos': pos, 'base_form': base_form, 'show_count':show_count, 'outlist': outlist}
    else:
        template_values = {'lex': '', 'gloss': '', 'pos': '', 'base_form': '', 'show_count':'10', 'outlist': []}

    return render(request, 'search.html', template_values)


def new_entry(request):
    if request.method == 'POST':
        lex = request.POST.get('lex')
        gloss = request.POST.get('gloss')
        pos = request.POST.get('pos')
        base_form = request.POST.get('base_form')
        outlist = fuzzy_search(lexicon, lex, gloss, pos, base_form)
        template_values = {'lex': lex, 'gloss': gloss, 'pos': pos, 'base_form': base_form, 'outlist': outlist}
        return render(request, 'new_entry.html', template_values)


def utilities(request):
    if request.method == 'GET':
        # template_values = {'upload_url': blobstore.create_upload_url('/upload')}
        template_values = {'upload_url': '/upload'}
        return render(request, 'utilities.html', template_values)
