# -*-coding: UTF-8-*-

from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from shortcuts import with_template

@with_template('hello/callback.html')
def oauth_callback(request):
    return {}

@login_required
@with_template('hello/welcome.html')
def logged_in(request):
    next = request.GET.get('next')
    if next:
        HttpResponseRedirect(next)

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

    return {}

@with_template('hello/please-log-in.html')
def login_form(request):
    if request.user.is_authenticated():
        next = request.GET.get('next', reverse('home'))
        return HttpResponseRedirect(next)

    return {}