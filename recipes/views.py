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
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from django.conf import settings

from recipes.models import *
from recipes.tasks import *
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

@with_template('recipes/remix-list.html')
def remix_list(request):
    """List of remixes, for the home page."""
    return {
        'remixes': Remix.objects.filter(withdrawn=None).order_by('recipe__label', '-modified'),
    }

@with_template('recipes/remix-detail.html')
def remix_detail(request, pk):
    """Info about one remix."""
    return {
        'remix': get_object_or_404(Remix, pk=pk)
    }

def remix_resource(request, pk, res_name):
    """A resource from a recipe pack."""
    remix = get_object_or_404(Remix, pk=int(pk, 10))
    data = remix.get_pack().get_resource(res_name).get_bytes()
    return HttpResponse(data, mimetype='image/png')

@with_template('recipes/remix-cooking.html')
def remix_cooking(request, pk):
    """User has requested creation of a texture pack."""
    remix = get_object_or_404(Remix, pk=int(pk, 10))
    if all(x.source_pack.is_ready() for x in remix.pack_args.all()):
        return HttpResponseRedirect(reverse('remix-edit', kwargs={'pk': remix.pk}))
    return {
        'remix': remix,
    }

@json_view
def remix_progress(request, pk):
    remix = get_object_or_404(Remix, pk=pk)
    steps = [
        {
            'name': 'arg_{0}'.format(arg.name),
            'label': 'Download {0}'.format(arg.source_pack),
            'percent': 100 if arg.source_pack.is_ready() else 0,
        }
        for arg in remix.pack_args.all()
    ]
    return {
        'success': True,
        'steps': steps,
        'percent': sum(x['percent'] for x in steps) / len(steps),
        'isComplete': all(x['percent'] for x in steps),
        'milliseconds': 15 * 1000,
        'href': reverse('pack', kwargs={'pk': remix.pk}),
        'label': remix.label,
    }

@with_template('recipes/remix-edit.html')
def remix_edit(request, pk):
    remix = get_object_or_404(Remix, pk=pk)
    class RemixEditForm(forms.ModelForm):
        class Meta:
            model = Remix
            fields = ['label', 'recipe']

    if request.method == 'POST':
        form = RemixEditForm(request.POST, instance=remix)
        if form.is_valid():
            remix2 = form.save()

            messages.add_message(request, messages.INFO,
                    u'Updated description of {remix}'.format(remix=remix2.label))
            return HttpResponseRedirect(reverse('remix-detail', kwargs={'pk': remix2.pk}))
    else:
        form = RemixEditForm(instance=remix)

    return {
        'remix': remix,
        'form': form,
        'recipes': Spec.objects.filter(spec_type='tprx'),
    }


def recipe(request, name):
    """Return the spec for a recipe as YAML or JSON."""
    recipe = get_object_or_404(Spec, name=name, spec_type='tprx')
    return HttpResponse(recipe.spec, mimetype="application/x-yaml")

def maps(request, name):
    """Return the spec for a map as YAML or JSON."""
    recipe = get_object_or_404(Spec, name=name, spec_type='tpmaps')
    return HttpResponse(recipe.spec, mimetype="application/x-yaml")

def make_texture_pack(request, pk, slug):
    """Generate the ZIP file for a texture pack."""
    remix = get_object_or_404(Remix, pk=pk)
    pack = remix.get_pack()

    response = HttpResponse(mimetype="application/zip")
    response['content-disposition'] = 'attachment; filename={file_name}'.format(
        file_name=slugify(remix.label) + '.zip'
    )
    pack.write_to(response)
    return response

@login_required
@with_template('recipes/beta-upgrade.html')
def beta_upgrade(request):
    # XXX This function is quite long.
    # Would it be possible to spin it out in to tasg

    suitable_recipes = Tag.objects.get(name='beta-13').spec_set.order_by('created')

    class BetaForm(forms.Form):
        pack_download_url = forms.URLField(max_length=1000, label='Download URL',
            help_text='URL to download the ZIP file')
        series_forum_url = forms.URLField(max_length=1000, required=False, label='Forum thread',
            help_text='URL of a forum thread about this texture pack')
        series_home_url = forms.URLField(max_length=1000, required=False, label='Home page',
            help_text='URL of a dedicated home page for this pack, if any')
        recipe = forms.ModelChoiceField(
            required=True,
            queryset=suitable_recipes,
            initial=Spec.objects.get(name='ersatz-beta-13'),
            help_text='Depends on whether the pack supports Beta 1.2 already')

    if request.method == 'POST': # If the form has been submitted...
        form = BetaForm(request.POST) # A form bound to the POST data
        if form.is_valid(): # All validation rules pass
            try:
                recipe = form.cleaned_data['recipe']
                download_url = form.cleaned_data['pack_download_url']
                source_pack = get_mixer().get_pack(download_url)

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
                    source_release = Release.objects.get(download_url=download_url)
                    messages.add_message(request, messages.INFO,
                            u'We already have an entry for {pack}'.format(pack=source_pack.label))
                except Release.DoesNotExist:
                    series = Source(
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
                ensure_source_pack_is_downloaded.delay(source_release.pk)

                remix = Remix(
                    owner=request.user,
                    label='{label} + Beta 1.3'.format(label=source_pack.label),
                    recipe=recipe)
                remix.save()
                remix.pack_args.create(
                    name='base',
                    source_pack=source_release)

                messages.add_message(request, messages.INFO,
                        u'Added {remix} to the queue'.format(remix=remix.label))

                return HttpResponseRedirect(
                    reverse('remix-cooking', kwargs={'pk': remix.pk})) # Redirect after POST
            except BadZipfile, err:
                messages.add_message(request, messages.ERROR,
                        u'The URL was valid but did not reference a texture pack ({err})'.format(err=err))
    else:
        form = BetaForm() # An unbound form

    return {
        'form': form,
        'recipes': suitable_recipes,
    }


@with_template('recipes/source-detail.html')
def source_series(request, pk):
    source_series = get_object_or_404(Source, pk=pk)
    releases = source_series.releases.order_by('-released')
    return {
        'source': source_series,
        'releases': releases,
        'release': releases[0],
    }

def source_resource(request, pk, release_pk, res_name):
    """A resource from a source pack."""
    source_pack = get_object_or_404(Release, pk=int(release_pk, 10))
    data = source_pack.get_pack().get_resource(res_name).get_bytes()
    return HttpResponse(data, mimetype='image/png')