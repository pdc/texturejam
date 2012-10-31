# -*-coding: UTF-8-*-

from celery.task import task

import re
from recipes.models import *
import hello.models

@task
def add(x, y):
    """Combine two addends additively and return their sum."""
    return x + y

@task(ignore_result=True)
def ensure_source_pack_is_downloaded(id):
    release = Release.objects.get(id=id)
    actual_pack = release.get_pack()
    actual_released = actual_pack.get_last_modified()
    if release.released != actual_released:
        release.released = actual_released
        release.save()


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

@task(ignore_result=True)
def download_and_remix(task_info_id):
    """Download the pack and create a source release, then combine with recipe to make remix."""
    task_info = DownloadTask.objects.get(id=task_info_id)

    source_pack = get_mixer().get_pack(task_info.download_url)
    label = source_pack.label
    m = LABEL_WITH_VERSION_RE.match(label)
    if m:
        series_label = m.group('series')
        release_label = m.group('release')
    else:
        series_label = label
        release_label = 'current'

    try:
        source_release = Release.objects.get(download_url=task_info.download_url)
    except Release.DoesNotExist:
        series = Source(
            owner=task_info.owner,
            label=series_label,
            home_url=task_info.home_url,
            forum_url=task_info.forum_url)
        series.save()
        source_release = series.releases.create(
            label=release_label,
            level=task_info.level,
            download_url=task_info.download_url,
            released=source_pack.get_last_modified())
    ensure_source_pack_is_downloaded(source_release.id)
    # Haven’t we just downlaoded that?
    # Yes, and I should have an API for just using the downloaded resouce.
    # But for now it gets it from HTTPD’s cache
    # so maybe it isn’t as bad as all that.

    remix = task_info.owner.remix_set.create(
        label='{label} + Patches'.format(label=source_pack.label),
        recipe=task_info.recipe)
    remix.pack_args.create(
        name='base',
        source_pack=source_release)

    task_info.remix = remix
    task_info.save()

@task(ignore_result=True)
def prepare_remix(remix_id):
    remix = Remix.objects.get(id=remix_id)
    if remix.is_ready():
        return

    remix.get_pack()
