from django.db import models
from django.contrib.auth.models import User

class Level(models.Model):
    label = models.CharField(max_length=200)
    desc = models.TextField()
    released = models.DateTimeField(help_text='When the curresponding version of Minecraft was released')

    def __unicode__(self):
        return self.label

class SourceSeries(models.Model):
    owner = models.ForeignKey(User, related_name='source_series')

    label = models.CharField(max_length=200)
    home_url = models.URLField(max_length=1000, blank=True)
    forum_url = models.URLField(max_length=1000, blank=True)

    created = models.DateTimeField(auto_now_add=True, help_text='When this series was added to our list')
    modified = models.DateTimeField(auto_now=True, help_text='When our info about this series was updated')

    def __unicode__(self):
        return self.label

class SourcePack(models.Model):
    series = models.ForeignKey(SourceSeries, related_name='releases')
    level = models.ForeignKey(Level, related_name='source_packs')

    label = models.CharField(max_length=200)
    download_url = models.URLField(max_length=1000)

    released = models.DateTimeField(auto_now_add=True, help_text='When this vesion of the pack was was released')

    def __unicode__(self):
        return '{series} {label}'.format(series=self.series.label, label=self.label)

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

class PackArg(models.Model):
    recipe_pack = models.ForeignKey(RecipePack, related_name='pack_args')
    source_pack = models.ForeignKey(SourcePack, related_name='occurrences')

    name = models.SlugField(help_text='Name used for ths formal parameter in the recipe')

    def __unicode__(self):
        return '{name}={source_pack}'.format(name=self.name, source_pack=self.source_pack.label)

