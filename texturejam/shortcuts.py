# -*-coding: UTF-8-*-

import re
import json
import httplib2

from django.http import HttpResponse
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.template.defaultfilters import slugify
from django.conf import settings


def with_template(default_template_name=None):
    """Decorator for view functions.

    The wrapped function should return a dictionary to use
    as template arguments.

    The dict can also include a template_name member to set
    which template is used to render the page.
    Otherwise default_template_name is used.

    If the function instead returns an HttpResponse,
    then that is returned verbatim.

    """
    def decorator(func):
        def decorated_func(request, *args, **kwargs):
            result = func(request, *args, **kwargs)
            if isinstance(result, HttpResponse):
                return result
            template_name = result.get('template_name', default_template_name)
            template_args = result
            return render_to_response(template_name, template_args,
                    context_instance=RequestContext(request))
        return decorated_func
    return decorator

def json_view(view_func):
    """Decorator for view functions retrning JSON.

    Thre wrapped function returns a dict that is rendered as JSON.
    """
    def wrapped_view(request, *args, **kwargs):
        result = view_func(request, *args, **kwargs)
        if isinstance(result, HttpResponse):
            return result
        return HttpResponse(json.dumps(result),
                mimetype='application/json')
    return wrapped_view

def texture_pack_view(view_func):
    """Decorator for view functions return a texture pack."""
    def wrapped_view(request, *args, **kwargs):
        result = view_func(request, *args, **kwargs)
        if isinstance(result, HttpResponse):
            return result
        response = HttpResponse(mimetype="application/zip")
        response['content-disposition'] = 'attachment; filename={file_name}'.format(
            file_name=slugify(result.label) + '.zip'
        )
        result.write_to(response)
        return response
    return wrapped_view


not_word_re = re.compile(r'\W+')
def name_from_label(s):
    return '_'.join(w for w in not_word_re.split(s.lower()) if w)

def static_context_processor(request):
    """Referenced in the setting TEMPLATE_CONTEXT_PROCESSORS to add link to static dir."""
    return {
        'static': settings.STATIC_URL,
    }

def redirect_field_value_context_processor(request):
    """Referenced in the setting TEMPLATE_CONTEXT_PROCESSORS to add link to static dir."""
    next = request.GET.get('next')
    if not next:
        next = request.get_full_path()
    if next == settings.LOGIN_REDIRECT_URL:
        next = '/'
    return {
        'redirect_field_value': next,
    }

def get_http():
    return httplib2.Http(settings.HTTPLIB2_CACHE_DIR)
