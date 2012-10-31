# Encoding: UTF-8

from django.core.management.base import BaseCommand, CommandError
from texturejam.recipes.models import *

class Command(BaseCommand):
    args = '<specs_dir>...'
    help = 'Creates or updates specs using on .tprx and .tpmaps files'

    def handle(self, *args, **options):
        for dir_path in args:
            self.stdout.write(dir_path + '... ')
            created_count, modified_count = update_specs_from_dir(dir_path)
            self.stdout.write('created {0}, modified {1}\n'.format(created_count, modified_count))