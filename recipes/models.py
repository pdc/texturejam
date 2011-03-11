# -*-coding: UTF-8-*-

import yaml
import re
from StringIO import StringIO
from django.db import models
from django.contrib.auth.models import User
from django.core.cache import cache
from django.conf import settings
from texturepacker import Mixer, RecipePack, Atlas, set_http_cache
import texturepacker

class Level(models.Model):
    label = models.CharField(max_length=200)
    desc = models.TextField()
    released = models.DateTimeField(help_text='When the curresponding version of Minecraft was released')

    def __unicode__(self):
        return self.label

class SourceSeries(models.Model):
    owner = models.ForeignKey(User, related_name='source_series')

    label = models.CharField(max_length=200)
    home_url = models.URLField(max_length=255, blank=True)
    forum_url = models.URLField(max_length=255, blank=True)

    created = models.DateTimeField(auto_now_add=True, help_text='When this series was added to our list')
    modified = models.DateTimeField(auto_now=True, help_text='When our info about this series was updated')

    def __unicode__(self):
        return self.label

class SourcePack(models.Model):
    series = models.ForeignKey(SourceSeries, related_name='releases')
    level = models.ForeignKey(Level, related_name='source_packs')

    label = models.CharField(max_length=200)
    download_url = models.URLField(max_length=255, unique=True)
    released = models.DateTimeField(help_text='When this vesion of the pack was was released')

    def __unicode__(self):
        return u'{series} {label}'.format(series=self.series.label, label=self.label)

class Spec(models.Model):
    owner = models.ForeignKey(User, related_name='atlases')

    label = models.CharField(max_length=200)
    name = models.SlugField(max_length=200)
    SPEC_TYPE_CHOICES = [
        ('tprx', 'Texture pack recipe'),
        ('tpmaps', 'Texture pack maps'),
    ]
    spec_type = models.CharField(max_length=100, choices=SPEC_TYPE_CHOICES)
    spec = models.TextField()

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return self.label

class RecipePack(models.Model):
    owner = models.ForeignKey(User, related_name='recipe_packs')
    recipe = models.ForeignKey(Spec, related_name='occurrences', limit_choices_to={'spec_type': 'tprx'})

    label = models.CharField(max_length=1000)

    created = models.DateTimeField(auto_now_add=True, help_text='When this pack was added to our list')
    modified = models.DateTimeField(auto_now=True, help_text='When our info about this pack was updated')

    def __unicode__(self):
        return self.label

    def get_cache_key(self):
        return 'entity-RecipePack-{pk}'.format(pk=self.pk)

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
                mixer.add_pack(arg.name, mixer.get_pack(arg.source_pack.download_url, base='internal:///'))
            spec = yaml.load(StringIO(self.recipe.spec))
            pack = mixer.make(spec, base='internal:///')


            # Why can't I cache pack objetcs dorectlt?
            strm = StringIO()
            pack.write_to(strm)

            cache.set(cache_key, (pack.get_last_modified(), strm.getvalue()))

        return pack

    def invalidate():
        cache.delete(self.get_cache_key())


class PackArg(models.Model):
    recipe_pack = models.ForeignKey(RecipePack, related_name='pack_args')
    source_pack = models.ForeignKey(SourcePack, related_name='occurrences')

    name = models.SlugField(help_text='Name used for ths formal parameter in the recipe')

    def __unicode__(self):
        return u'{name}={source_pack}'.format(name=self.name, source_pack=self.source_pack.label)


def get_mixer():
    """Get a Texturepacker mixer that knows about locally hosted resources.

    This allows the server to avoid making HTTP
    requests to itself.
    """
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