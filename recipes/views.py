# -*-coding: UTF-8-*-

from StringIO import StringIO
import yaml
import re

from django.http import HttpResponse
from django.template import RequestContext
from django.shortcuts import render_to_response, get_object_or_404
from django.conf import settings

from recipes.models import *
from shortcuts import *

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