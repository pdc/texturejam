# -*-coding: UTF-8-*-

from celery.task import task

from recipes.models import *
import hello.models

@task
def add(x, y):
    """Combine two addends additively and return their sum."""
    return x + y

@task(ignore_result=True)
def ensure_source_pack_is_downloaded(pk):
    source_pack = SourcePack.objects.get(pk=pk)
    actual_pack = source_pack.get_pack()
