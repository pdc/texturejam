# -*-coding: UTF-8-*-

import sys
import os
import yaml
import re
from datetime import datetime, timedelta
from StringIO import StringIO
from django import forms
from django.db import models
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.cache import cache
from django.conf import settings
from texturepacker import Mixer, Atlas, set_http_cache
import texturepacker

# Using South to manage migrations.
#
# After adding or changing fields run the following
# in the deve environment:
#
#     ./manage.py schemamigration recipes --auto
#
# And then in each environemtn do
#
#     ./manage.py migrate recipes
#

class Level(models.Model):
    class Meta:
        get_latest_by = 'released'
        ordering = ['-released'] # Reverse chronological order

    label = models.CharField(max_length=200)
    desc = models.TextField()
    released = models.DateTimeField(help_text='When the curresponding version of Minecraft was released')

    def __unicode__(self):
        return self.label

class Tag(models.Model):
    label = models.CharField(max_length=200, help_text='Name of the tag with the desired capitalization')
    name = models.SlugField(max_length=200, unique=True, help_text='Uniquely identifies this tag in the database')

    def __unicode__(self):
        return self.label

class WrongSpecType(Exception):
    pass

class Spec(models.Model):
    class Meta:
        unique_together = [('name', 'spec_type')]
        ordering = ['spec_type', 'label']

    owner = models.ForeignKey(User)
    tags = models.ManyToManyField(Tag, blank=True)

    label = models.CharField(max_length=200, help_text="Identifies this recipe to users")
    desc = models.TextField(blank=True, help_text="Explians this recipe to users; can use Markdown formatting")

    name = models.SlugField(max_length=200, help_text="Identifies this spec in recipes; should be unique")
    SPEC_TYPE_CHOICES = [
        ('tprx', 'Texture pack recipe'),
        ('tpmaps', 'Texture pack maps'),
    ]
    spec_type = models.CharField(max_length=100, choices=SPEC_TYPE_CHOICES)

    spec = models.TextField(help_text="The recipe code in YAML or JSON format.")

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return self.label

    def has_tag(self, tag):
        """Has this spec been tagged with this tag?"""
        tag_name = tag.name if isinstance(tag, Tag) else tag
        return self.tags.filter(name=tag_name).count()

    def get_internal_url(self):
        """The URL that can be used within recipes to refer to this spec."""
        base = 'internal:///' if self.spec_type == 'tprx' else 'internal:///{0}/'.format(self.spec_type[2:])
        return '{base}{name}'.format(base=base, name=self.name)

    def get_atlas(self):
        """If this spec is for an atlas (type==tpmaps), then return the atlas."""
        if self.spec_type != 'tpmaps':
            raise WrongSpecType('{name}: is {type}, not a maps spec'.format(name=self.name, type=self.spec_type))
        spec = yaml.load(StringIO(self.spec))
        return get_mixer().get_atlas(spec, self.get_internal_url())

    def get_alt_tiles(self):
        tile_groups = []
        map = self.get_atlas().get_map('terrain.png', 'internal:///')
        for group_name, cellss in map.get_alts_list():
            tiless = []
            for cells in cellss:
                tiles = []
                for cell, label in zip(cells, ['Std', 'Alt'] + ['Alt {x}'.format(x=i + 2) for i in range(len(cells) - 2)]):
                    tile = {
                        'name': cells[0],
                        'value': cell,
                        'label': label,
                        'style': map.get_css(cell),
                    }
                    tiles.append(tile)
                tiless.append(tiles)
            tile_groups.append((group_name, tiless))
        return tile_groups


class Source(models.Model):
    owner = models.ForeignKey(User)

    label = models.CharField(max_length=200, help_text="Not including version number")
    home_url = models.URLField(max_length=255, blank=True,
        verbose_name='Home page URL', help_text="Web page or site about  this pack (optional)")
    forum_url = models.URLField(max_length=255, blank=True,
        verbose_name='Forum URL', help_text="Where discussion of this pack takes place (optional)")

    created = models.DateTimeField(auto_now_add=True, help_text='When this series was added to our list')
    modified = models.DateTimeField(auto_now=True, help_text='When our info about this series was updated')

    def __unicode__(self):
        return self.label

    def truncated_home_url(self):
        return trunc_url(self.home_url)

    def truncated_forum_url(self):
        return trunc_url(self.forum_url)

class Release(models.Model):
    """Represents one release of the source series.

    Generally there need only be exactly one release for
    a given source. I split it in to two models
    to allow for the rare case when older versions of a
    pack are specifically rquired by some recipe.
    """
    class Meta:
        get_latest_by = 'released'
        ordering = ['-released']

    series = models.ForeignKey(Source, related_name='releases')
    level = models.ForeignKey(Level, related_name='source_packs')
    maps = models.ForeignKey(Spec, blank=True, null=True,
        limit_choices_to={'spec_type': 'tpmaps'},
        on_delete=models.SET_NULL)

    label = models.CharField(max_length=200)
    download_url = models.URLField(max_length=255, unique=True)
    released = models.DateTimeField(help_text='When this vesion of the pack was was released')

    last_download_attempt = models.DateTimeField(help_text='When the system last tried to fetch this pack.',
        editable=False, default=datetime.fromtimestamp(0))

    def __unicode__(self):
        return u'{series} {label}'.format(series=self.series.label, label=self.label)

    def get_file_path(self):
        return os.path.join(settings.RECIPES_SOURCE_PACKS_DIR, str(self.pk) + '.zip')

    def is_ready(self):
        """Is this pack ready to be used in recipes?

        At present this means it has been downloaded,
        and the release date has not been set later than
        when the download was performed.
        """
        file_path = self.get_file_path()
        return self.last_download_attempt >= self.released and os.path.exists(file_path)

    def invalidate_downloaded_data(self):
        file_path = self.get_file_path()
        if os.path.exists(file_path):
            os.unlink(file_path)

    def get_pack(self, loader=None):
        file_path = self.get_file_path()
        if not self.is_ready():
            if self.download_url.startswith(settings.STATIC_URL):
                static_path = os.path.join(settings.STATIC_DIR,
                    self.download_url[len(settings.STATIC_URL):].strip('/'))
                os.symlink(static_path, file_path)
            else:
                if not loader:
                    loader = get_loader()
                self.last_download_attempt = datetime.now()
                self.save()
                bytes = loader.get_bytes(self.download_url, base='internal:///')
                with open(file_path, 'wb') as strm:
                    strm.write(bytes)
        return texturepacker.SourcePack(file_path, Atlas())

    def truncated_download_url(self):
        return trunc_url(self.download_url)

    def active_occurrences(self):
        return self.occurrences.filter(recipe_pack__withdrawn=None)


class Remix(models.Model):
    class Meta:
        verbose_name_plural = 'Remixes'

    owner = models.ForeignKey(User)
    recipe = models.ForeignKey(Spec, related_name='occurrences', limit_choices_to={'spec_type': 'tprx'})

    label = models.CharField(max_length=1000)

    created = models.DateTimeField(auto_now_add=True, editable=False, help_text='When this pack was added to our list')
    modified = models.DateTimeField(auto_now=True, editable=False, help_text='When our info about this pack was updated')

    withdrawn_reason = models.CharField(max_length=200, blank=True, default='', help_text='One-line description of why this remix was withdrawn, or (more commonly) empty if is has not been withdrawn')
    withdrawn = models.DateTimeField(null=True, blank=True, help_text='When this remix was withdrawn, or (more commonly) blank if it has not been withdrawn')

    def __unicode__(self):
        return self.label

    def get_cache_key(self):
        return 'entity-Remix-{pk}'.format(pk=self.pk)

    def get_pack(self):
        """Get the pack object represented by this entity.

        Pack is cached to try to avoid rebuilding it too often.
        """
        pack = None

        cache_key = self.get_cache_key()
        pr = cache.get(cache_key)
        if pr:
            last_modified, pack_bytes = pr
            if last_modified >= self.modified:
                pack = texturepacker.SourcePack(StringIO(pack_bytes), Atlas())

        if not pack:
            set_http_cache(settings.HTTPLIB2_CACHE_DIR)
            mixer = get_mixer()
            for arg in self.pack_args.all():
                mixer.add_pack(arg.name, arg.source_pack.get_pack(mixer.loader))
            spec = yaml.load(StringIO(self.recipe.spec))
            pack = mixer.make(spec, base='internal:///')

            # Why can't I cache pack objects directly?
            strm = StringIO()
            pack.write_to(strm)

            cache.set(cache_key, (pack.get_last_modified(), strm.getvalue()))

        return pack

    def invalidate():
        cache.delete(self.get_cache_key())

    def get_base_release(self):
        candidates = self.pack_args.filter(name='base')
        if candidates:
            return candidates[0].source_pack

class PackArg(models.Model):
    class Meta:
        unique_together = [('recipe_pack', 'name')]

    recipe_pack = models.ForeignKey(Remix, related_name='pack_args')
    source_pack = models.ForeignKey(Release, related_name='occurrences')

    name = models.SlugField(help_text='Name used for this formal parameter in the recipe')

    def __unicode__(self):
        return u'{name}={source_pack}'.format(name=self.name, source_pack=self.source_pack.label)

class DownloadTask(models.Model):
    owner = models.ForeignKey(User)
    recipe = models.ForeignKey(Spec, limit_choices_to={'spec_type': 'tprx'})
    level = models.ForeignKey(Level)
    remix = models.ForeignKey(Remix, blank=True, null=True, help_text='The remix, created once the resource is downloaded.')

    download_url = models.URLField(max_length=255, unique=True)
    home_url = models.URLField(max_length=255, blank=True)
    forum_url = models.URLField(max_length=255, blank=True)

    created = models.DateTimeField(auto_now_add=True, editable=False, help_text='When this pack was added to our list')
    modified = models.DateTimeField(auto_now=True, editable=False, help_text='When our info about this pack was updated')

    problem = models.CharField(max_length=1000, blank=True, help_text='A problem preventing the remix from being created. Blank means it is OK')

    def is_finished(self):
        return self.remix and self.remix.id

    def get_progress(self):
        """Return a list of dicts describing progress so far.

        This is potentially a list of steps wqith a percentage-done for each.
        """
        progress = [{
            'name': 'download_1',
            'label': 'Downloads {0}'.format(self.download_url),
            'percent': 100 if self.is_finished() else 1,
        },
        {
            'name': 'mixing',
            'label': 'Creates remix',
            'percent': 100 if self.is_finished() else 0,
        }]
        return progress

def get_loader():
    loader = texturepacker.Loader()
    augment_loader(loader)
    return loader

def augment_loader(loader):
    """Add local knowledge to this loader.

    This allows for certain HTTP resources to be
    fetched directly from disc.
    """
    loader.add_local_knowledge(settings.STATIC_URL, settings.STATIC_DIR)

    def fetch_spec(path):
        if path.startswith('///maps/'):
            spec = Spec.objects.get(spec_type='tpmaps', name=path[8:])
        elif path.startswith('///'):
            spec = Spec.objects.get(spec_type='tprx', name=path[3:])
        else:
            raise Exception('Could not fetch %r' % (path,))
        return {'content-type': 'application/x-yaml'}, StringIO(spec.spec)
    loader.add_scheme('internal', fetch_spec)

def get_mixer():
    """Get a Texturepacker mixer that knows about locally hosted resources.

    This allows the server to avoid making HTTP
    requests to itself.
    """
    mixer = Mixer()
    augment_loader(mixer.loader)
    return mixer



URL_RE = re.compile("""
    ^
    (?: https? | ftp ) :
    //
    (?: www\. )?
    ( [\w.-]+ )
    ( /.*? )?
    (
        (?: /[^/]+)
    )?
    ( / | /index.\w+ )?
    $
""", re.VERBOSE)

def trunc_url(u):
    m = URL_RE.match(u)
    ps = [m.group(1)]
    if m.group(2) and m.group(3):
        ps.append(u'/…')
    elif m.group(2) and m.group(2) != '/':
        ps.append(m.group(2))
    if m.group(3):
        ps.append(m.group(3))
    if m.group(4):
        ps.append('/')
    return ''.join(ps)