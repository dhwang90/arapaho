from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect, HttpResponse

def helloworld(request):
    return HttpResponse("Hello World :)")#request.META["REMOTE_USER"])

def main_page(request):
    username = "User"
    if request.method == 'GET':
        template_values = {
            'username': username
        }

    elif request.method == 'POST':
        username = request.POST.get('content')
        template_values = {
            'username': username
        }
    return render_to_response('hellouser/hello_page.html', template_values, context_instance=RequestContext(request))


def next_page(request):
    if request.method == 'POST':

        username = request.POST.get('content')
        color = request.POST.get('color')
        template_values = {
            'username': username,
            'color': color,
        }
        return render_to_response('hellouser/goodbye_page.html', template_values, context_instance=RequestContext(request))
    return HttpResponseRedirect('/')


def goodbye_page(request):
    if request.method == 'POST':
        return HttpResponseRedirect('/')
