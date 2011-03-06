# -*-coding: UTF-8-*-

from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from shortcuts import with_template

@with_template('hello/callback.html')
def oauth_callback(request):
    return {}

@login_required
@with_template('hello/welcome.html')
def logged_in(request):
    next = request.GET.get('next')
    if next:
        messages.add_message(request, messages.INFO,
            'Welcome to Texturejam, {name}!'.format(name=(user.get_full_name() or user.username)))
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

@with_template('hello/test-messages.html')
def test_messages(request):
    messages.add_message(request, messages.INFO,
        'Short info')
    messages.add_message(request, messages.ERROR,
        'Short error')
    messages.add_message(request, messages.INFO,
        'Long info: Cras porta aliquet euismod. Sed iaculis, nisi id hendrerit euismod, metus lacus ornare elit, nec gravida velit eros nec risus. Lorem ipsum dolor sit amet, consectetur adipiscing elit. Vestibulum dictum blandit tellus, vel eleifend erat vulputate ut. ')
    messages.add_message(request, messages.ERROR,
        'Long error: Nulla porta molestie interdum. Phasellus vel sollicitudin turpis. Nunc pharetra lacinia vehicula. Aenean volutpat semper massa, sed consectetur urna faucibus sollicitudin. Duis scelerisque mi quam. Donec tempor magna vel purus bibendum laoreet. Vestibulum ante ipsum primis in faucibus orci luctus et ultrices posuere cubilia Curae; Phasellus sollicitudin augue ac dui ultricies varius mollis mi dapibus. Mauris cursus velit sed sem elementum iaculis porta sapien iaculis. Pellentesque habitant morbi tristique senectus et netus et malesuada fames ac turpis egestas. Aliquam nec mauris dolor.')
    return {}
