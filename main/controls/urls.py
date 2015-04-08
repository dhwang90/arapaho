from django.conf.urls import patterns, include, url
#from hellouser.views import helloworld, main_page, goodbye_page, next_page
import lexicon.views

urlpatterns = patterns('',
    # test urls
    # url(r'^$',helloworld),
    # url(r'^hellouser/$', main_page),
    # url(r'^hellouser/name/$', main_page),
    # url(r'^hellouser/color/$', next_page),
    # url(r'^hellouser/color/goodbye/$', goodbye_page),

    # lexicon urls
    url(r'utilities', lexicon.views.utilities, name='Utilities'),
    url(r'search', lexicon.views.search, name='Search'),
    url(r'entry', lexicon.views.modify_entry, name='Modify Entry'),
    # url(r'upload', views.upload_handler, name='Upload Handler'),
    # url(r'dictionary', views.toolbox_serve_handler, name='Toolbox Serve Handler'),
    # url(r'modifyform', views.modify_form_handler, name='Modify Form Handler'),
    # url(r'newform', views.new_form_handler, name='New Form Handler'),
    # url(r'modify_feedback', views.entry_feedback_handler, name='Entry Feedback Handler'),
    # url(r'entry', views.entry_handler, name='Entry Handler'),
    url(r'^$', lexicon.views.main_handler, name='Main Handler'),
)
