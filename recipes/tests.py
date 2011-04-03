# -*-coding: UTF-8-*-

"""
This file demonstrates two different styles of tests (one doctest and one
unittest). These will both pass when you run "manage.py test".

Replace these with more appropriate tests for your application.
"""

from django.test import TestCase
from textwrap import dedent
from recipes.models import *

class TruncUrlTests(TestCase):
    def test_no_www(self):
        self.assertEqual(u'example.org/…/baz.quux', trunc_url('http://example.org/foo/bar/baz.quux'))

    def test_yes_www(self):
        self.assertEqual(u'example.com/…/baz.quux', trunc_url('http://www.example.com/foo/bar/baz.quux'))

    def test_strip_index(self):
        self.assertEqual(u'example.com/…/bar/', trunc_url('http://www.example.com/foo/bar/index.html'))

    def test_strip_index_php(self):
        self.assertEqual(u'example.com/…/bar/', trunc_url('http://www.example.com/foo/bar/index.php'))

    def test_just_a_slash(self):
        self.assertEqual('example.net', trunc_url('http://www.example.net/'))

    def test_single_pathicle(self):
        self.assertEqual('example.net/stomp', trunc_url('http://www.example.net/stomp'))

    def test_https(self):
        self.assertEqual('example.eu', trunc_url('https://www.example.eu/'))

    def test_missing_path(self):
        self.assertEqual('example.org.uk', trunc_url('https://www.example.org.uk'))

    def test_ftp(self):
        self.assertEqual(u'example.co.uk/…/smuersh', trunc_url('ftp://www.example.co.uk/bunkum/smuersh'))

class GetMapTests(TestCase):
    def test_get_grid_map(self):
        spec = Spec(spec_type='tpmaps', spec=dedent("""
            bank/instruments.png:
                source_rect:
                    width: 32
                    height: 32
                cell_rect:
                    width: 16
                    height: 16
                names:
                    - banjo
                    - ukelele
                    - sousaphone
                    - tambourine
        """))
        atlas = spec.get_atlas()
        map = atlas.get_map('bank/instruments.png', None)
        self.assertTrue(map)
        self.assertEqual((16, 16, 32, 32), map.get_box('tambourine'))

    def test_not_a_maps(self):
        with self.assertRaises(WrongSpecType):
            spec = Spec(spec_type='tprx', spec="foo")
            atlas = spec.get_atlas()

class SpecTests(TestCase):
    def test_get_internal_url_maps(self):
        spec = Spec(name='alphonse', spec_type='tpmaps', spec="href: http://example.com/foo.tpmaps")
        spec.save()
        self.assertEqual('internal:///maps/alphonse', spec.get_internal_url())

    def test_get_internal_url_recope(self):
        spec = Spec(name='bart', spec_type='tprx', spec="label: bunk")
        spec.save()
        self.assertEqual('internal:///bart', spec.get_internal_url())