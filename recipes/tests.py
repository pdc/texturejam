# -*-coding: UTF-8-*-

"""
This file demonstrates two different styles of tests (one doctest and one
unittest). These will both pass when you run "manage.py test".

Replace these with more appropriate tests for your application.
"""

from django.test import TestCase
from mock import patch, Mock

import shutil
import json
from textwrap import dedent
from recipes.models import *
from django.contrib.auth.models import User
from django.conf import settings

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

class TextureCellTests(TestCase):
    def test_it(self):
        map = texturepacker.GridMap((32, 32), (16, 16), ['ape', 'bee', 'ape_1', 'ape_2'])
        atlas = texturepacker.Atlas()
        atlas.add_map('terrain.png', map)

        spec = Spec()
        spec.save()

        with patch.object(spec, 'get_atlas') as mock_get_atlas:
            mock_get_atlas.return_value = atlas
            tile_infos = spec.get_alt_tiles()

        (group_name, tiless), = tile_infos
        self.assertEqual('ape', group_name)
        tiles, = tiless

        self.assertEqual('ape', tiles[0]['name'])
        self.assertEqual('ape', tiles[0]['value'])
        self.assertEqual('Std', tiles[0]['label'])
        self.assertEqual('width: 16px; height: 16px; background-position: 0 0;', tiles[0]['style'])

        self.assertEqual('ape', tiles[1]['name'])
        self.assertEqual('ape_1', tiles[1]['value'])
        self.assertEqual('Alt', tiles[1]['label'])
        self.assertEqual('width: 16px; height: 16px; background-position: 0 -16px;', tiles[1]['style'])

        self.assertEqual('ape', tiles[2]['name'])
        self.assertEqual('ape_2', tiles[2]['value'])
        self.assertEqual('Alt 2', tiles[2]['label'])
        self.assertEqual('width: 16px; height: 16px; background-position: -16px -16px;', tiles[2]['style'])

class TestUploader(TestCase):
    TEST_DIR = 'test_working'
    def setUp(self):
        if os.path.exists(self.TEST_DIR):
            shutil.rmtree(self.TEST_DIR)
        os.mkdir(self.TEST_DIR)
        os.mkdir(os.path.join(self.TEST_DIR, 'maps'))

        with open(os.path.join(self.TEST_DIR, 'hello.tprx'), 'wb') as strm:
            json.dump({'hello': 'world'}, strm, indent=True)

        with open(os.path.join(self.TEST_DIR, 'maps/mappemonde.tpmaps'), 'wb') as strm:
            json.dump({'terrain.png': 'w00t'}, strm, indent=True)

        User.objects.create(username='jak', password='x', is_staff=False)
        User.objects.create(username='jil', password='x', is_staff=True)

    def test_nothing(self):
        # This just checks that the setUp routine works!
        pass

    def test_created_count(self):
        created_count, modified_count = update_specs_from_dir(self.TEST_DIR)
        self.assertEqual(2, created_count)
        self.assertEqual(0, modified_count)

    def test_created_recipe(self):
        update_specs_from_dir(self.TEST_DIR)
        recipe = Spec.objects.get(name='hello', spec_type='tprx')
        self.assertEqual({'hello': 'world'}, json.loads(recipe.spec))

    def test_has_owner(self):
        update_specs_from_dir(self.TEST_DIR)
        recipe = Spec.objects.get(name='hello', spec_type='tprx')
        self.assertEqual('jil', recipe.owner.username)

    def test_created_atlas(self):
        update_specs_from_dir(self.TEST_DIR)
        atlas_entity = Spec.objects.get(name='mappemonde', spec_type='tpmaps')
        self.assertEqual({'terrain.png': 'w00t'}, json.loads(atlas_entity.spec))

    def test_updates_existing_recipe(self):
        # One of the specs already exists.
        spec0 = Spec.objects.create(owner=User.objects.get(username='jak'),
            name='hello', spec_type='tprx', spec=json.dumps({'hello': 'sailor'}))

        created_count, modified_count = update_specs_from_dir(self.TEST_DIR)
        self.assertEqual(1, created_count)
        self.assertEqual(1, modified_count)

        recipe = Spec.objects.get(name='hello', spec_type='tprx')
        self.assertEqual({'hello': 'world'}, json.loads(recipe.spec))
        self.assertEqual('jak', recipe.owner.username)
        self.assertTrue(recipe.modified > spec0.modified)

        # Just to be sure we have not accidentally created a spare object.
        # (In practice the uniquenbess rules will prevent this anyway.)
        self.assertEqual(2, Spec.objects.count())

    def test_idempotent(self):
        # This time the old content matches the file content.
        spec0 = Spec.objects.create(owner=User.objects.get(username='jak'),
            name='hello', spec_type='tprx', spec=json.dumps({'hello': 'world'}, indent=1))

        created_count, modified_count = update_specs_from_dir(self.TEST_DIR)
        self.assertEqual(1, created_count)
        self.assertEqual(0, modified_count)

        recipe = Spec.objects.get(name='hello', spec_type='tprx')
        self.assertEqual({'hello': 'world'}, json.loads(recipe.spec))
        self.assertEqual('jak', recipe.owner.username)
        self.assertEqual(spec0.modified, recipe.modified)

        self.assertEqual(2, Spec.objects.count())

    def test_ersatz_label(self):
        update_specs_from_dir(self.TEST_DIR)
        recipe = Spec.objects.get(name='hello', spec_type='tprx')
        self.assertEqual('Hello', recipe.label)

    def test_preserve_existing_label(self):
        spec0 = Spec.objects.create(owner=User.objects.get(username='jak'),
            name='hello', label='GREETINGS', spec_type='tprx', spec=json.dumps({'hello': 'sailor'}))

        update_specs_from_dir(self.TEST_DIR)
        recipe = Spec.objects.get(name='hello', spec_type='tprx')
        self.assertEqual('GREETINGS', recipe.label)

    def test_repair_missing_owner(self):
        spec0 = Spec.objects.create(name='hello', label='GREETINGS', spec_type='tprx', spec=json.dumps({'hello': 'sailor'}))

        created_count, modified_count = update_specs_from_dir(self.TEST_DIR)
        self.assertEqual(1, created_count)
        self.assertEqual(1, modified_count)

        recipe = Spec.objects.get(name='hello', spec_type='tprx')
        self.assertEqual('jil', recipe.owner.username)

class TestAnonymous(TestCase):
    def test_anonymous_created(self):
        user = get_anonymous()
        self.assertTrue(user)
        self.assertTrue(isinstance(user, User))

        self.assertEqual('anonymous', user.username)
        self.assertFalse(user.has_usable_password())
        self.assertTrue(user.id)

    def test_anonymous_created_only_once(self):
        user1 = get_anonymous()
        user2 = get_anonymous()

        self.assertEqual(user1, user2)
        self.assertEqual(1, User.objects.count())

class TestInstantUgrade(TestCase):
    def setUp(self):
        # Create a recipe and a source to apply it to.
        level = Level.objects.create(label='One')
        recipe = Spec.objects.create(name='foo', label='Foo', spec='foo', spec_type='tprx')
        level.upgrade_recipe = recipe
        level.save()

        source = Source.objects.create(label='Bar', owner=get_anonymous())
        source.releases.create(download_url='http://example.org/bar.zip', level=level, label='1.0')

        self.source = source
        self.recipe = recipe
        self.level = level

    def test_get_instant_upgrade(self):
        # If not user supplied, replace with the anonymous user.
        upgrade = self.source.get_instant_upgrade(None)
        self.assertTrue(isinstance(upgrade, Remix))
        self.assertEqual(self.recipe, upgrade.recipe)
        for arg in upgrade.pack_args.all():
            self.assertEqual(self.source.latest_release(), arg.source_pack)
            self.assertEqual('base', arg.name)
        self.assertEqual(get_anonymous(), upgrade.owner)

    def test_instant_owned_upgrade(self):
        # If someone is logged in, ownership of the instant upgrade goes to them.
        user = User.objects.create(username='quux')
        upgrade = self.source.get_instant_upgrade(user)
        self.assertEqual(user, upgrade.owner)


class SourceTests(TestCase):
    def setUp(self):
        self.dir = 'test_working'
        if os.path.exists(self.dir):
            shutil.rmtree(self.dir)
        os.mkdir(self.dir)


        self.user = User.objects.create(username='bob')
        self.source = self.user.source_set.create(label='foo', )
        self.release = self.source.releases.create(download_url='http://example.com/foo.zip',
            released=datetime.now() + timedelta(days=-1))

    @patch.object(settings, 'RECIPES_SOURCE_PACKS_DIR', '/foo/bar')
    def test_file_name(self):
        # Each release has a file to store its cached copy in.
        self.assertEqual('/foo/bar/source1-release1.zip', self.release.get_file_path())

    def test_is_not_ready_if_no_file(self):
        with patch.object(settings, 'RECIPES_SOURCE_PACKS_DIR', self.dir):
            self.assertFalse(self.release.is_ready())

    def test_is_not_ready_if_file_is_stale(self):
        with open(self.release.get_file_path(), 'w') as strm:
            strm.write('foo')
        with patch.object(settings, 'RECIPES_SOURCE_PACKS_DIR', self.dir):
            self.assertFalse(self.release.is_ready())

    @patch('texturepacker.SourcePack')
    def test_get_pack(self, mock_cls):
        with patch.object(settings, 'RECIPES_SOURCE_PACKS_DIR', self.dir):
            # Using mock loader & siurce pack class
            loader = Mock(name='loader')
            loader.get_bytes.return_value = 'woot'
            pack = self.release.get_pack(loader=loader)
            pack2 = self.release.get_pack(loader=loader)

            # Check that the pack was downloaded.
            loader.get_bytes.assert_once_called_with('http://example.com/foo.zip', 'internal:///')
            with open(self.release.get_file_path(), 'rb') as strm:
                self.assertEqual('woot', strm.read())

            # Check it was used to create source pack.
            for i in range(2):
                self.assertEqual(self.release.get_file_path(), mock_cls.call_args_list[i][0][0])
                self.assertTrue(isinstance(mock_cls.call_args_list[i][0][1], texturepacker.Atlas))

            # Finally, the entity knows it is loaded.
            self.assertTrue(self.release.is_ready())




