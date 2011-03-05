# -*-coding: UTF-8-*-

import yaml
import re

from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render_to_response, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.conf import settings

from recipes.models import *
from recipes.forms import *
from shortcuts import *

@with_template('recipes/packs.html')
def recipe_pack_list(request):
    """List of recipe packs, for the home page."""
    return {
        'recipe_packs': RecipePack.objects.all(),
    }

def recipe(request, name):
    """Return the spec for a recipe as YAML or JSON."""
    recipe = get_object_or_404(Spec, name=name, spec_type='tprx')
    return HttpResponse(recipe.spec, mimetype="application/x-yaml")

def maps(request, name):
    """Return the spec for a map as YAML or JSON."""
    recipe = get_object_or_404(Spec, name=name, spec_type='tpmaps')
    return HttpResponse(recipe.spec, mimetype="application/x-yaml")

def make_texture_pack(request, pk):
    """Generate the ZIP file for a texture pack."""
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

@login_required
@with_template('recipes/beta-upgrade.html')
def beta_upgrade(request):
    if request.method == 'POST': # If the form has been submitted...
        form = BetaForm(request.POST) # A form bound to the POST data
        if form.is_valid(): # All validation rules pass
            # Which recipe?
            source_pack = get_mixer().get_pack(form.cleaned_data['pack_download_url'])
            if 'gui/items.png' in source_pack.get_resource_names():
                recipe_name = 'ersatz-beta-13'
            else:
                recipe_name = 'ersatz-beta-13-sans-items'
            recipe = Spec.objects.get(name=recipe_name)

            level = Level.objects.get(label='Beta 1.2')

            series = SourceSeries(
                owner=request.user,
                label=form.cleaned_data['series_label'],
                home_url=form.cleaned_data['series_home_url'],
                forum_url=form.cleaned_data['series_forum_url'])
            series.save()
            source_pack_entity = series.releases.create(
                label=form.cleaned_data['pack_label'],
                level=level,
                download_url=form.cleaned_data['pack_download_url'],
                released=form.cleaned_data['pack_released'] or datetime.now())

            recipe_pack = RecipePack(
                owner=request.user,
                label='{pack} + Beta 1.3'.format(pack=source_pack_entity.label),
                recipe=recipe)
            recipe_pack.save()
            recipe_pack.pack_args.create(
                name='beta12',
                source_pack=source_pack_entity)

            return HttpResponseRedirect('/') # Redirect after POST
    else:
        form = BetaForm() # An unbound form

    return {
        'form': form,
    }