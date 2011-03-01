# -*-coding: UTF-8-*-

from StringIO import StringIO
import yaml
import re

from django.http import HttpResponse
from django.template import RequestContext
from django.shortcuts import render_to_response, get_object_or_404
from django.conf import settings

from texturepacker import Mixer
from recipes.models import *

def with_template(default_template_name=None):
    def decorator(func):
        def decorated_func(request, *args, **kwargs):
            result = func(request, *args, **kwargs)
            if isinstance(result, HttpResponse):
                return result
            template_name = result.get('template_name', default_template_name)
            template_args = {'static': settings.STATIC_URL}
            template_args.update(result)
            return render_to_response(template_name, template_args,
                    context_instance=RequestContext(request))
        return decorated_func
    return decorator


not_word_re = re.compile(r'\W+')
def name_from_label(s):
    return '_'.join(not_word_re.split(s.lower()))

###


@with_template('recipes/packs.html')
def recipe_pack_list(request):
    return {
        'recipe_packs': RecipePack.objects.all(),
    }

def recipe(request, name):
    recipe = get_object_or_404(Spec, name=name, spec_type='tprx')
    return HttpResponse(recipe.spec, mimetype="application/x-yaml")

def maps(request, name):
    recipe = get_object_or_404(Spec, name=name, spec_type='tpmaps')
    return HttpResponse(recipe.spec, mimetype="application/x-yaml")

def get_mixer():
    mixer = Mixer()
    def fetch_spec(path):
        if path.startswith('///maps/'):
            spec = Spec.objects.get(spec_type='tpmaps', name=path[8:])
        elif path.startswith('///'):
            spec = Spec.objects.get(spec_type='tprx', name=path[3:])
        else:
            raise Exception('Could not fetch %r' % (path,))
        return {'content-type': 'application/x-yaml'}, StringIO(spec.spec)
    mixer.loader.add_scheme('internal', fetch_spec)
    return mixer

def make_texture_pack(request, pk):
    recipe_pack = get_object_or_404(RecipePack, pk=pk)
    mixer = get_mixer()
    for arg in recipe_pack.pack_args.all():
        mixer.add_pack(arg.name, mixer.get_pack(arg.source_pack.download_url, base='internal:///'))
    spec = yaml.load(StringIO(recipe_pack.recipe.spec))
    pack = mixer.make(spec, base='internal:///')
    response = HttpResponse(mimetype="application/zip")
    response['content-disposition'] = 'attachment; filename={file_name}'.format(
        file_name=name_from_label(recipe_pack.label) + '.zip'
    )
    pack.write_to(response)
    return response