from django.conf.urls import patterns, include, url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
import lexicon.views

urlpatterns = patterns('',
    # lexicon urls
    url(r'^index$', lexicon.views.index_handler, name='index_handler'),
    url(r'^$', lexicon.views.index_handler, name='index_handler'),


    url(r'main$', lexicon.views.main_handler, name='main_handler'),

    url(r'^utilities$', lexicon.views.utilities, name='utilities'),

    url(r'^search/search$', lexicon.views.search, name='search'),
    url(r'^search$', lexicon.views.search, name='search'),

    url(r'^get_lex/', lexicon.views.get_lex, name='get_lex'),

    url(r'^batch_modify$', lexicon.views.batch_modify, name='batch_modify'),
    url(r'^batch_entry$', lexicon.views.batch_entry, name='batch_entry'),

    url(r'^entry/(?P<editmode>\w+)/$',lexicon.views.modify_entry, name='entry'),

    #url(r'^adjudicate/(?P<manual_reload>\w+)$',lexicon.views.adjudicate, name='load_adjudications'),
    #url(r'^adjudicate/(?P<prev_viewed_user>\w+)/(?P<prev_viewed_date>[a-zA-Z0-9_\-]+)/$', lexicon.views.adjudicate, name='adjudicate'),
    #url(r'^adjudicate$', lexicon.views.adjudicate, name='adjudicate'),

    url(r'^adjudicate_select$', lexicon.views.adjudicate_select, name='adjudicate_select'),
    url(r'^adjudicate_file/(?P<filename>[a-zA-Z0-9_\-]+)/(?P<status>[NP])/$', lexicon.views.adjudicate_file, name='adjudicate_file'),
    url(r'^adjudicate_select$', lexicon.views.adjudicate_select, name='adjudicate_select'),

    url(r'^end_session$', lexicon.views.end_session, name='commit_session'),
    url(r'^commit_adjudication/(?P<filename>[a-zA-Z0-9_\-]+)/$', lexicon.views.commit_adjudication, name='commit_adjudication'),

    url(r'^renew_lexicon$', lexicon.views.renew_lexicon, name='renew_lexicon'),
    url(r'^reload_user', lexicon.views.reload_user, name='reload_user'),

    url(r'^cleartemp$', lexicon.views.clear_temp, name='clear_temp'),

    url(r'^public/view_search$', lexicon.views.view_search, name='view_search'),

    #url(r'^temp/temp_allolex$', lexicon.views.temp_allolex, name='temp_allolex'),
    #url(r'^temp/temp_allolex_manual$', lexicon.views.temp_allolex_manual, name='temp_allolex_manual'),
    #url(r'^temp/temp_allolex_new$', lexicon.views.temp_allolex_new, name='temp_allolex_new'),


)

urlpatterns += staticfiles_urlpatterns()
