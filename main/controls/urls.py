from django.conf.urls import patterns, include, url
from hellouser.views import helloworld, main_page, goodbye_page, next_page

urlpatterns = patterns('',
    # test urls
    url(r'^$',helloworld),
    url(r'^hellouser/$', main_page),
    url(r'^hellouser/name/$', main_page),
    url(r'^hellouser/color/$', next_page),
    url(r'^hellouser/color/goodbye/$', goodbye_page),
)
