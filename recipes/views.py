# -*-coding: UTF-8-*-

import yaml
import re
import errno
from datetime import datetime, timedelta
from zipfile import BadZipfile
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseNotAllowed
from django.template import RequestContext
from django.shortcuts import render_to_response, get_object_or_404
from django.core.urlresolvers import reverse
from django.template.defaultfilters import slugify
from django.utils.safestring import mark_safe
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from django.conf import settings

from recipes.models import *
from recipes.tasks import *
from shortcuts import *

@with_template('recipes/remix-list.html')
def remix_list(request):
    """List of remixes, for the home page."""
    try:
        alts_tag = Tag.objects.get(name='alts')
        maps_for_alts = alts_tag.spec_set.filter(spec_type='tpmaps').order_by('label')
    except Tag.DoesNotExist:
        maps_for_alts = None

    # Can't work out how to do this with filters, so:
    beta_remixes = {}
    other_remixes = {}
    misc_remixes = []
    for remix in Remix.objects.filter(withdrawn=None).order_by('label'):
        if remix.recipe.has_tag('upgrade'):
            beta_remixes.setdefault(remix.recipe.id, []).append(remix)
        else:
            release = remix.get_base_release()
            if release:
                other_remixes.setdefault(release.series.id, []).append(remix)
            else:
                misc_remixes.append(remix)

    #beta_remixes_1 = [(xs[0].recipe, xs) for (k, xs) in beta_remixes.items()]
    #beta_remixes_1.sort(key=lambda (r, xs): r.label, reverse=True)

    other_remixes_1 = [(xs[0].get_base_release(), xs) for (k, xs) in other_remixes.items() if len(xs) > 1]
    other_remixes_1.sort(key=lambda (r, xs): r.series.created, reverse=True)

    for xs in other_remixes.values():
        if len(xs) == 1:
            misc_remixes.extend(xs)
    misc_remixes_1 = [('More' if len(misc_remixes) > 1 else 'One more', misc_remixes)] if misc_remixes else []

    upgraded = []
    upgradeable = []
    for source in Source.objects.all().order_by('label'):
        if source.upgrade_remix:
            upgraded.append(source)
        elif source.is_upgrade_remix_needed:
            upgradeable.append(source)

    return {
        #'beta_remixes': beta_remixes_1,
        'other_remixes': other_remixes_1 + misc_remixes_1,
        'maps_for_alts': maps_for_alts,
        'upgraded_sources': upgraded,
        'upgradeable_sources': upgradeable,
    }

@with_template('recipes/remix-detail.html')
def remix_detail(request, remix_id):
    """Info about one remix."""
    remix = get_object_or_404(Remix, id=remix_id)
    if not remix.is_ready() and (not remix.queued or remix.queued < datetime.now() + timedelta(seconds=-300)):
        try:
            prepare_remix.delay(remix.id)
            messages.add_message(request, messages.INFO,
                u'Added {remix} to the queue.'.format(remix=remix.label))
        except IOError, e:
            msg = e
            if e.errno == 61: # Connection refused
                msg = 'The AMQP server is not running'
            messages.add_message(request, messages.ERROR,
                u'Could not add {remix} to the queue: {msg}'.format(
                    remix=remix,
                    msg=msg,
                ))
    return {
        'remix': remix,
        'task_info': remix,
        'progress_json': reverse('remix-progress-json', kwargs={'remix_id': remix.id}),
    }

@json_view
def remix_progress_json(request, remix_id):
    remix = get_object_or_404(Remix, id=remix_id)
    steps = remix.get_progress()
    return {
        # Whether this call succeeded: NOT whether the remix is finished!
        'success': True,

        # The steps remaining and overall completedness.
        'steps': steps,
        'percent': sum(x['percent'] for x in steps) / len(steps),
        'isComplete': all(x['percent'] == 100 for x in steps),

        # Wait this long before asking againb & use this URL next time.
        'milliseconds': 3 * 1000,
        'next': reverse('remix-progress-json', kwargs={'remix_id': remix.id}),

        # If successful then these will describe the link to the result.
        'href': remix.is_ready and reverse('remix-detail', kwargs={'remix_id': remix.id}),
        'label': remix.is_ready and remix.label,
    }


def remix_resource(request, remix_id, resource_name):
    """A resource from a recipe pack."""
    remix = get_object_or_404(Remix, id=remix_id)
    data = remix.get_pack().get_resource(resource_name).get_bytes()
    return HttpResponse(data, mimetype='image/png')

def instant_upgrade(request, source_id):
    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])
    source = get_object_or_404(Source, id=source_id)
    remix = source.upgrade_remix()
    if remix:
        messages.add_message(request, messages.INFO,
            u'That remix has already been created')
        return HttpResponseRedirect(reverse('remix-detail', kwargs={'remix_id': remix.id}))
    if not source.is_upgrade_remix_needed:
        messages.add_message(request, messages.INFO,
            u'We don’t need to create an pgraded remix of {source}.'.format(source=source))
        return HttpResponseRedirect(reverse('source-detail', kwargs={'source_id': source.id}))
    remix = source.get_instant_upgrade(request.user)
    return HttpResponseRedirect(reverse('remix-detail', kwargs={'remix_id': remix.id}))

@with_template('recipes/download-task-progress.html')
def download_task_progress(request, task_id):
    """User has requested creation of a texture pack."""
    task_info = get_object_or_404(DownloadTask, id=task_id)
    if task_info.is_finished():
        return HttpResponseRedirect(reverse('remix-edit', kwargs={'remix_id': task_info.remix.id}))
    return {
        'task_info': task_info,
        'progress_json': reverse('download-task-progress-json', kwargs={'task_id': task_info.id}),
    }

@json_view
def download_task_progress_json(request, task_id):
    task_info = get_object_or_404(DownloadTask, id=task_id)
    steps = task_info.get_progress()
    return {
        # Whether this call succeeded: NOT whether the remix is finished!
        'success': True,

        # The steps remaining and overall completedness.
        'steps': steps,
        'percent': sum(x['percent'] for x in steps) / len(steps),
        'isComplete': all(x['percent'] == 100 for x in steps),

        # Wait this long before asking againb & use this URL next time.
        'milliseconds': 3 * 1000,
        'next': reverse('download-task-progress-json', kwargs={'task_id': task_id}),

        # If successful then these will describe the link to the result.
        'href': task_info.remix and reverse('remix-detail', kwargs={'remix_id': task_info.remix.id}),
        'label': task_info.remix and task_info.remix.label,
    }

@with_template('recipes/remix-edit.html')
def remix_edit(request, remix_id):
    remix = get_object_or_404(Remix, id=remix_id)

    if remix.owner.id != request.user.id:
        messages.add_message(request, messages.ERROR,
            u'You can’t edit {remix}, because you are not its maintainer'.format(remix=remix.label))
        return HttpResponseRedirect(reverse('remix-detail', kwargs={'remix_id': remix.id}))

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
            return HttpResponseRedirect(reverse('remix-detail', kwargs={'remix_id': remix2.id}))
    else:
        form = RemixEditForm(instance=remix)

    return {
        'remix': remix,
        'form': form,
        'recipes': Spec.objects.filter(spec_type='tprx'),
    }

def spec(request, name, spec_type):
    """Return the spec for a recipe as YAML or JSON."""
    spec = get_object_or_404(Spec, name=name, spec_type=spec_type)
    if request.method == 'PUT':
        return HttpResponseForbidden()
        # XXX check is valid YAML
        # XXX check content-type

        etag = request.META.get('IF_MATCH')
        if etag != spec.get_etag():
            return HttpResponse(status=412,
                content='Etag did not match', content_type="text/plain")

        spec.spec = request.raw_post_data
        spec.save()
        response = HttpResponse(status=204)
        response['ETag'] = spec.get_etag()
        return response
    response = HttpResponse(spec.spec, mimetype="application/x-yaml")
    response['ETag'] = spec.get_etag()
    return response


def make_texture_pack(request, remix_id, slug):
    """Generate the ZIP file for a texture pack."""
    remix = get_object_or_404(Remix, id=remix_id)
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

    suitable_recipes = Tag.objects.get(name='upgrade').spec_set.order_by('-label')
    default_recipe = suitable_recipes[0]

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
            initial=default_recipe,
            help_text='Depends on the version of Minecraft this pack already supports')

    if request.method == 'POST': # If the form has been submitted...
        form = BetaForm(request.POST) # A form bound to the POST data
        if form.is_valid(): # All validation rules pass
            try:
                recipe = form.cleaned_data['recipe']
                download_url = form.cleaned_data['pack_download_url']
                home_url = form.cleaned_data['series_home_url']
                forum_url = form.cleaned_data['series_forum_url']

                level = recipe.level
                try:
                    task_info = DownloadTask.objects.get(download_url=download_url)
                    if task_info.owner == request.user:
                        messages.add_message(request, messages.INFO,
                            'You have already requested this remix')
                    else:
                        messages.add_message(request, messages.INFO,
                            '{other} has already requested this remix'.format(other=task_info.user))
                except DownloadTask.DoesNotExist:
                    task_info = request.user.downloadtask_set.create(
                        recipe=recipe,
                        level=level,
                        download_url=download_url,
                        home_url=home_url,
                        forum_url=forum_url)
                download_and_remix.delay(task_info.id)
                messages.add_message(request, messages.INFO,
                        u'Download starting …')

                return HttpResponseRedirect(
                    reverse('download-task-progress', kwargs={'task_id': task_info.id})) # Redirect after POST
            except BadZipfile, err:
                messages.add_message(request, messages.ERROR,
                        u'The URL was valid but did not reference a texture pack ({err})'.format(err=err))
            except IOError, err:
                if err.errno == errno.ECONNREFUSED:
                    messages.add_message(request, messages.ERROR,
                            u'Could not queue your request (it seems the AMQP service is down)')
                else:
                    messages.add_message(request, messages.ERROR,
                            u'Could not queue your request ({cls}: {msg})'.format(
                            cls=err.__class__.__name__, msg=err))

    else:
        form = BetaForm() # An unbound form

    return {
        'form': form,
        'recipes': suitable_recipes,
    }

@with_template('recipes/source-list.html')
def source_list(request, tag_names_plusified):
    tag_names = [x for x in tag_names_plusified.split('+') if x]
    sources = Source.objects.all()
    if tag_names:
        sources = sources.filter(tags__name__in=tag_names)
    sources = sources.order_by('label')
    return {
        'tag_names_plusified': tag_names_plusified,
        'tag_names': tag_names,
        'tags': Tag.objects.filter(name__in=tag_names),
        'sources': sources,
    }

@with_template('recipes/source-detail.html')
def source_detail(request, source_id):
    source = get_object_or_404(Source, id=source_id)
    releases = source.releases.order_by('-released')
    release = releases[0]
    return {
        'source': source,
        'releases': releases,
        'release': releases[0],
    }

@with_template('recipes/source-edit.html')
def source_edit(request, source_id):
    source = get_object_or_404(Source, id=source_id)

    if source.owner.id != request.user.id:
        messages.add_message(request, messages.ERROR,
            u'You can’t edit {source} because you are not its maintainer'.format(source=source.label))
        return HttpResponseRedirect(reverse('source-detail', kwargs={'source_id': source.id}))

    releases = source.releases.order_by('-released')
    release = releases[0]

    class SourceEditForm(forms.Form):
        source_label = forms.CharField(max_length=200,
            label='Pack name',
            help_text='Without version number')
        release_label = forms.CharField(max_length=200,
            label='Latest release',
            help_text='Version number of most recent release of pack')
        release_download_url = forms.CharField(max_length=1000,
            label='Download URL',
            help_text='URL for downloading the ZIP file')
        release_level = forms.ModelChoiceField(Level.objects.all(),
            label='Minecraft version',
            help_text='Latest version of Minecraft this pack supports')
        source_forum_url = forms.CharField(max_length=1000,
            required=False,
            label='Forum thread',
            help_text='URL where this pack is discussed')
        source_home_url = forms.CharField(max_length=1000,
            required=False,
            label='Home page',
            help_text='URL of a dedicated home page for this pack, if any')

    if request.method == 'POST':
        form = SourceEditForm(request.POST)
        if form.is_valid():
            source_label = form.cleaned_data['source_label']
            source_forum_url = form.cleaned_data['source_forum_url']
            source_home_url = form.cleaned_data['source_home_url']
            needs_save = (source_label != source.label
                    or source_forum_url != source.forum_url
                    or source_home_url != source.home_url)
            if needs_save:
                source.label = source_label
                source.forum_url = source_forum_url
                source.home_url = source_home_url
                source.full_clean(exclude=['owner', 'created', 'modified'])
                source.save()
                messages.add_message(request, messages.INFO,
                        u'Updated description of {source}'.format(source=source.label))

            release_label = form.cleaned_data['release_label']
            release_download_url = form.cleaned_data['release_download_url']
            release_level = form.cleaned_data['release_level']
            if release_download_url == release.download_url:
                # Same release; might still want to edit label or level
                needs_save = (release_label != release.label
                        or release_level.id != release.level.id)
                if needs_save:
                    release.label = release_label
                    release.level = release_level
                    release.full_clean(exclude=['released', 'last_download_attempt'])
                    release.save()
                    release.invalidate_downloaded_data()
                    ensure_source_pack_is_downloaded.delay(release.id)
                    messages.add_message(request, messages.INFO,
                        u'Updated description of release {release}'.format(release=release.label))
            else:
                # New release
                old_release = release
                release = source.releases.create(
                    label=release_label,
                    level=release_level,
                    download_url=release_download_url,
                    released=datetime.now())
                ensure_source_pack_is_downloaded.delay(release.id)
                for arg in PackArg.objects.filter(source_pack=old_release):
                    arg.source_pack = release
                    arg.save()
                messages.add_message(request, messages.INFO,
                    u'Added new release {release}'.format(release=release.label))

            return HttpResponseRedirect(reverse('source-detail', kwargs={'source_id': source.id}))
    else:
        form = SourceEditForm(initial={
            'source_label': source.label,
            'release_label': release.label,
            'release_download_url': release.download_url,
            'release_level': release.level,
            'source_forum_url': source.forum_url,
            'source_home_url': source.home_url,
        })

    return {
        'form': form,
        'source': source,
        'releases': releases,
        'release': releases[0],
    }

def source_resource(request, source_id, release_id, resource_name):
    """A resource from a source pack."""
    release = get_object_or_404(Release, series__id=source_id, id=release_id)
    data = release.get_pack().get_resource(resource_name).get_bytes()
    return HttpResponse(data, mimetype='image/png')

@login_required
@with_template('recipes/recipe-from-maps.html')
def recipe_from_maps(request, id):
    spec = get_object_or_404(Spec, id=id)
    tiles_list = spec.get_alt_tiles()

    release = spec.release_set.latest('released')
    src = reverse('source-resource', kwargs={'source_id': release.series.id, 'release_id': release.id, 'resource_name': 'terrain.png'})

    # Lets see if I can build my own dynamic form!
    class RecipeFromMapsForm(forms.Form):
        label = forms.CharField(max_length=200,
                help_text='A name for this recipe. It should be unique.')
        desc = forms.CharField(max_length=2000,
                widget=forms.Textarea(attrs={'rows': 3}),
                required=False, label='Description',
                help_text='Describes this recipe to other users. Separate paragraphs wth blank lines. Markdown formatting is supporterd.')

        def __init__(self, tiles_list, src, *args, **kwargs):
            super(RecipeFromMapsForm, self).__init__(*args, **kwargs)
            for name, tiless in tiles_list:
                for tiles in tiless:
                    choices = [(x['value'],
                        mark_safe('<i id="{id}">&nbsp;</i> {label}'.format(
                            id='sample_{0}'.format(x['value']),
                            label=x['label']
                        ))) for x in tiles]
                    self.fields[tiles[0]['name']] = forms.ChoiceField(choices=choices, widget=forms.RadioSelect)

    if request.method == 'POST':
        form = RecipeFromMapsForm(tiles_list, src, request.POST)
        if form.is_valid():
            label = form.cleaned_data['label']
            desc = form.cleaned_data['desc']
            rx_struct = {
                'label': label,
                'desc': desc,
                'parameters': {
                    'packs': ['base']
                },
                'maps': spec.get_internal_url(),
                'mix':  {
                    'pack': '$base',
                    'files': [
                        # XXX pack.png?
                        '*.png',
                        {
                            'file': 'terrain.png',
                            'replace': {
                                'cells': {ts[0]['name']: form.cleaned_data[ts[0]['name']]
                                    for (gn, tss) in tiles_list
                                    for ts in tss
                                }
                            }
                        }
                    ]
                }
            }
            strm = StringIO()
            yaml.dump(rx_struct, strm, default_flow_style=False, encoding=None, width=72, indent=4)
            rx_str = strm.getvalue()
            rx_spec, was_created = request.user.spec_set.get_or_create(
                name='{user}/{label}'.format(user=request.user.username, label=slugify(label)),
                spec_type='tprx')
            rx_spec.label = label
            rx_spec.desc = desc
            rx_spec.spec = rx_str
            rx_spec.save()

            messages.add_message(request, messages.INFO,
                u'{created} recipe {label}'.format(created='Created' if was_created else 'Updated', label=label))

            for release in spec.release_set.all():
                remix, was_created = request.user.remix_set.get_or_create(
                    recipe=rx_spec,
                    pack_args__source_pack=release,
                    defaults={u'label': u'{source} + {recipe}'.format(recipe=label, source=release.series.label)})
                remix.save()
                arg, _ = remix.pack_args.get_or_create(name='base', defaults={'source_pack': release})
                arg.source_pack = release
                arg.save()
                messages.add_message(request, messages.INFO,
                    u'{created} remix {label}'.format(
                        created='Created' if was_created else 'Updated',
                        label=remix.label))
            return HttpResponseRedirect(reverse('remix-edit', kwargs={'remix_id': remix.id}))
    else:
        initial = {'label': '{maps} Alts'.format(maps=spec.label)}
        for name, tiless in tiles_list:
            for tiles in tiless:
                try:
                    tile = tiles[1]
                    initial[tile['name']] = tile['value']
                except ValueError:
                    pass
        form = RecipeFromMapsForm(tiles_list, src, initial=initial)

    return {
        'spec': spec,
        'form': form,
        'tiles_list': tiles_list,
        'src': src,
    }