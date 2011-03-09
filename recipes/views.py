# -*-coding: UTF-8-*-

import yaml
import re
from datetime import datetime, timedelta
from zipfile import BadZipfile
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render_to_response, get_object_or_404
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings

from recipes.models import *
from recipes.forms import *
from shortcuts import *

LABEL_WITH_VERSION_RE = re.compile(ur"""
    ^
    (?P<series> .*)
    (?:
        \s*
        (?: , | - )?
        \s+
        (?P<release>
            [vr]?
            \d+
            (?: \. \d* )*
            (?: [a-z] \d* )?
        )
    )
    $
""", re.VERBOSE | re.IGNORECASE)

@with_template('recipes/packs.html')
def recipe_pack_list(request):
    """List of recipe packs, for the home page."""
    return {
        'recipe_packs': RecipePack.objects.order_by('-modified'),
    }

@with_template('recipes/pack.html')
def recipe_pack_detail(request, pk):
    """Info about one recipe pack."""
    recipe_pack = get_object_or_404(RecipePack, pk=int(pk, 10))
    return {
        'pack': recipe_pack,
    }

def recipe_pack_resource(request, pk, res_name):
    """A resource from a recipe pack."""
    recipe_pack = get_object_or_404(RecipePack, pk=int(pk, 10))
    return HttpResponse(recipe_pack.get_pack().get_resource(res_name).get_bytes(), mimetype='image/png')

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
    pack = recipe_pack.get_pack()

    response = HttpResponse(mimetype="application/zip")
    response['content-disposition'] = 'attachment; filename={file_name}'.format(
        file_name=name_from_label(recipe_pack.label) + '.zip'
    )
    pack.write_to(response)
    return response

@login_required
@with_template('recipes/beta-upgrade.html')
def beta_upgrade(request):
    # XXX This function is quite long.
    # Would it be possible to spin it out in to the model?
    if request.method == 'POST': # If the form has been submitted...
        form = BetaForm(request.POST) # A form bound to the POST data
        if form.is_valid(): # All validation rules pass
            # Which recipe?
            try:
                download_url = form.cleaned_data['pack_download_url']
                source_pack = get_mixer().get_pack(download_url)
                if 'gui/items.png' in source_pack.get_resource_names():
                    recipe_name = 'ersatz-beta-13'
                else:
                    recipe_name = 'ersatz-beta-13-sans-items'
                recipe = Spec.objects.get(name=recipe_name)

                level = Level.objects.get(label='Beta 1.2')

                label = source_pack.label
                m = LABEL_WITH_VERSION_RE.match(label)
                if m:
                    series_label = m.group('series')
                    release_label = m.group('release')
                else:
                    series_label = label
                    release_label = ''

                try:
                    source_release = SourcePack.objects.get(download_url=download_url)
                    messages.add_message(request, messages.INFO,
                            'we already have an entry for {pack}'.format(pack=source_pack.label))
                except SourcePack.DoesNotExist:

                    series = SourceSeries(
                        owner=request.user,
                        label=series_label,
                        home_url=form.cleaned_data['series_home_url'],
                        forum_url=form.cleaned_data['series_forum_url'])
                    series.save()
                    source_release = series.releases.create(
                        label=release_label,
                        level=level,
                        download_url=form.cleaned_data['pack_download_url'],
                        released=source_pack.get_last_modified())

                recipe_pack = RecipePack(
                    owner=request.user,
                    label='{label} + Beta 1.3'.format(label=source_pack.label),
                    recipe=recipe)
                recipe_pack.save()
                recipe_pack.pack_args.create(
                    name='beta12',
                    source_pack=source_release)

                messages.add_message(request, messages.INFO,
                        'Created {recipe_pack}'.format(recipe_pack=recipe_pack.label))

                return HttpResponseRedirect(
                    reverse('pack', kwargs={'pk': recipe_pack.pk})) # Redirect after POST
            except BadZipfile, err:
                messages.add_message(request, messages.ERROR, 'The URL was valid but did not reference a texture pack ({err})'.format(err=err))
    else:
        form = BetaForm() # An unbound form

    return {
        'form': form,
    }