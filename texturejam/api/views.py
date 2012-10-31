# -*-coding: UTF-8-*-

import yaml
import re
from datetime import datetime, timedelta
from zipfile import BadZipfile
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render_to_response, get_object_or_404
from django.core.urlresolvers import reverse
from django.template.defaultfilters import slugify
from django.utils.safestring import mark_safe
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from django.conf import settings

from texturejam.recipes.models import *
from texturejam.recipes.tasks import *
from texturejam.shortcuts import *

@json_view
def index_page(request):
    return {
        'version': 0,
        'urls': {
            'spec_by_name': '/api/specs/{type}/{name}',
        }
    }

@json_view
def spec_page(request, name, type):
    spec = get_object_or_404(Spec, name=name, spec_type=type)
    return {
        'label': spec.label,
        'etag': spec.get_etag(),

        'pub': ('/rx/' if type == 'tprx' else '/rx/maps/') + name,
        'edit': '/api/specs/{type}/{name}/content',
    }