# -*-coding: UTF-8-*-

from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.contrib import auth
from shortcuts import with_template

@with_template('hello/callback.html')
def oauth_callback(request):
    return {}

@with_template('hello/welcome.html')
def logged_in(request):
    return {
        'hello': dir(request.user.social_auth),
        'world': request.user.social_auth.__class__.__name__,
    }

@with_template('hello/oh-dear.html')
def login_error(request):
    return {}

@with_template('hello/log-out.html')
def log_out(request):
    if request.method == 'POST':
        auth.logout(request)
        next = request.GET.get('next', reverse('home'))
        return HttpResponseRedirect(next)
    else:
        return {}
