# -*-coding: UTF-8-*-

from celery.task import task

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
