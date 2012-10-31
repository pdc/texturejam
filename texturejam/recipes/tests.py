# -*-coding: UTF-8-*-

"""
This file demonstrates two different styles of tests (one doctest and one
unittest). These will both pass when you run "manage.py test".

Replace these with more appropriate tests for your application.
"""

from django.test import TestCase
from mock import patch, Mock
from unittest import skip

import shutil
import json
from textwrap import dedent
from texturejam.recipes.models import *
import texturejam.recipes.models as recipe_models_module
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
        spec = Spec(name='alphonse', spec_type='tpmaps', spec="href: http://example.com/foo.tpmaps",
                owner=User.objects.create(username='USER'))
        spec.save()
        self.assertEqual('internal:///maps/alphonse', spec.get_internal_url())

    def test_get_internal_url_recope(self):
        spec = Spec(name='bart', spec_type='tprx', spec="label: bunk",
                owner=User.objects.create(username='USER'))
        spec.save()
        self.assertEqual('internal:///bart', spec.get_internal_url())

class TextureCellTests(TestCase):
    def test_it(self):
        map = texturepacker.GridMap((32, 32), (16, 16), ['ape', 'bee', 'ape_1', 'ape_2'])
        atlas = texturepacker.Atlas()
        atlas.add_map('terrain.png', map)

        owner = User.objects.create(username='USERNAME')
        spec = Spec(owner=owner)
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

    @skip('Test for fixing a problem it is now difficult to reproduce')
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
        level = Level.objects.create(label='One', released=datetime(2012, 10, 31))
        owner = User.objects.create(username='USERNAME')
        recipe = Spec.objects.create(owner=owner, name='foo', label='Foo', spec='foo', spec_type='tprx')
        level.upgrade_recipe = recipe
        level.save()

        source = Source.objects.create(label='Bar', owner=get_anonymous())
        source.releases.create(download_url='http://example.org/bar.zip', level=level, label='1.0', released=datetime(2012,10,31))

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
        self.assertTrue(upgrade.label)

    def test_instant_owned_upgrade(self):
        # If someone is logged in, ownership of the instant upgrade goes to them.
        user = User.objects.create(username='quux')
        upgrade = self.source.get_instant_upgrade(user)
        self.assertEqual(user, upgrade.owner)


class SourceTests(TestCase):
    dir = 'test_working'

    def setUp(self):
        self.dir = 'test_working'
        if os.path.exists(self.dir):
            shutil.rmtree(self.dir)
        os.mkdir(self.dir)

        self.level = Level.objects.create(released=datetime(2012, 10, 31))
        self.user = User.objects.create(username='bob')
        self.source = self.user.source_set.create(label='foo', )
        self.release = self.source.releases.create(download_url='http://example.com/foo.zip',
            level=self.level,
            released=datetime.now() + timedelta(days=-1))

    @patch.object(settings, 'RECIPES_SOURCE_PACKS_DIR', '/foo/bar')
    def test_file_name(self):
        # Each release has a file to store its cached copy in.
        self.assertEqual('/foo/bar/source1-release1.zip', self.release.get_file_path())

    @patch.object(settings, 'RECIPES_SOURCE_PACKS_DIR', dir)
    def test_is_not_ready_if_no_file(self):
        self.assertFalse(self.release.is_ready())

    @patch.object(settings, 'RECIPES_SOURCE_PACKS_DIR', dir)
    def test_is_not_ready_if_file_is_stale(self):
        with open(self.release.get_file_path(), 'w') as strm:
            strm.write('foo')
        self.assertFalse(self.release.is_ready())

    @patch.object(settings, 'RECIPES_SOURCE_PACKS_DIR', dir)
    @patch('texturepacker.SourcePack')
    def test_get_pack(self, mock_cls):
        # Using mock loader & source pack class
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

class RemixDownloadingTests(TestCase):
    dir = 'test_working'

    def setUp(self):
        if os.path.exists(self.dir):
            shutil.rmtree(self.dir)
        os.mkdir(self.dir)

        # Create a source pack ...
        self.level = Level.objects.create(released=datetime(2012, 10, 31))
        self.user = User.objects.create(username='bob')
        self.source = self.user.source_set.create(label='foo')
        self.release = self.source.releases.create(download_url='http://example.com/foo.zip',
            released=datetime.now() + timedelta(days=-1),
            level=self.level)

        # ... and a remix that uses it.
        self.recipe_spec = {
            'label': 'herp',
            'desc': 'derp'
        }
        self.recipe = Spec.objects.create(owner=self.user, spec=json.dumps(self.recipe_spec), name='herp', spec_type='tprx')
        self.remix = self.user.remix_set.create(recipe=self.recipe)
        self.remix.pack_args.create(name='base', source_pack=self.release)

    def test_fixture(self):
        pass

    @patch.object(settings, 'RECIPES_SOURCE_PACKS_DIR', dir)
    def test_unready(self):
        self.assertFalse(self.remix.is_ready())

    @patch.object(settings, 'RECIPES_SOURCE_PACKS_DIR', dir)
    def test_progress_before_download(self):
        progress = self.remix.get_progress()

        self.assertDictContainsSubset({
            'label': 'Download example.com/foo.zip',
            'percent': 1}, progress[0])
        self.assertTrue(progress[0]['name'])

    @patch.object(settings, 'RECIPES_SOURCE_PACKS_DIR', dir)
    @patch.object(recipe_models_module, 'get_mixer')
    @patch('texturepacker.SourcePack')
    def test_progress_after_download(self, MockSourcePack, mock_get_mixer):
        # So muck mocking!
        loader = Mock()
        loader.get_bytes.return_value = 'foo'
        pack = Mock()
        mock_mixer = Mock()
        mock_get_mixer.return_value = mock_mixer
        mock_mixer.make.return_value = pack

        # Finally ready to push the button!
        result = self.remix.get_pack(loader)
        self.assertEqual(1, len(MockSourcePack.call_args_list))
        self.assertEqual('test_working/source1-release1.zip', MockSourcePack.call_args_list[0][0][0])
        mock_mixer.make.assert_called_once_with(self.recipe_spec, base='internal:///')
        self.assertEqual(pack, result)

        # Should now report 100% progress.
        progress = self.remix.get_progress()

        self.assertDictContainsSubset({
            'label': 'Download example.com/foo.zip',
            'percent': 100}, progress[0])
        self.assertTrue(progress[0]['name'])

class InstantAlternatesRecipeTests(TestCase):
    def test_recipe_from_alts(self):
        alts = [('cat', [['cat_front', 'cat_front_1'], ['cat_side', 'cat_side_1'], ['cat_top', 'cat_top_1']])]
        code = 'a_a'
        self.assertEqual({'cells': {'cat_front': 'cat_front_1', 'cat_top': 'cat_top_1'}},
            recipe_fragment_from_alt_code(alts, code))

    def test_code_from_from_data(self):
        alts = [('cat', [['cat', 'cat1']]), ('dog', [['dog', 'dog1']])]
        form_data = {'cat': 'cat1', 'dog': 'dog'}
        self.assertEqual('a_', alt_code_from_form_data(alts, form_data))

    def test_alt_desc_from_code_2(self):
        alts = [('cat', [['cat', 'cat_1']]), ('dog_hog', [['dog_hog', 'dog_hog_1', 'dog_hog_2']]), ('eel_fox', [['eel_fox', 'eel_fox_1', 'eel_fox_2']])]
        code = 'ab_'
        self.assertEqual('Alt cat and dog hog (2)', desc_from_alt_code(alts, code))

    def test_alt_desc_from_code_3(self):
        alts = [('cat', [['cat', 'cat_1']]), ('dog_hog', [['dog_hog', 'dog_hog_1', 'dog_hog_2']]), ('eel_fox', [['eel_fox', 'eel_fox_1', 'eel_fox_2']])]
        code = 'aba'
        self.assertEqual('Alt cat, dog hog (2), and eel fox', desc_from_alt_code(alts, code))

    @patch.object(recipe_models_module, 'get_mixer')
    def test_to_construction(self, mock_get_mixer):
        # Create some test objects...
        level = Level.objects.create(label='topmost', released=datetime(2012, 10, 31))
        user = User.objects.create(username='USER')
        maps = Spec.objects.create(owner=user, name='shazam', spec_type='tpmaps', spec=json.dumps({
            'terrain.png': {
                'source_rect': {'width': 16, 'height': 32},
                'cell_rect': {'width': 8, 'height': 8},
                'names': [
                    'ape', 'bee'
                    'cat', 'cat_1',
                    'dog_hog', 'dog_hog_1', 'dog_hog_2',
                    'eel_fox', 'eel_fox_1', 'eel_fox_2']}}))
        source = Source.objects.create(label=u'Foo’s bar pack (Alt)', owner=get_anonymous())
        release = source.releases.create(download_url='http://example.org/bar.zip', maps=maps, level=level, label='1.0',
                released=datetime(2012, 10, 31))
        code = '_ba'

        # ... and some mock obects ...
        mock_loader = Mock()
        mock_loader.maybe_get_spec.return_value = json.loads(maps.spec)
        mixer = texturepacker.Mixer(loader=mock_loader)
        mock_get_mixer.return_value = mixer
        with patch.object(release, 'get_pack') as mock_get_pack:
            mock_get_pack.return_value = 'JUMP'

            self.assertEqual('JUMP', release.get_pack())

            with patch.object(mixer, 'make') as mock_make:
                with patch.object(mixer, 'add_pack') as mock_add_pack:
                    mock_make.return_value = 'THE PACK'

                    # Checking the mocks work as expected
                    self.assertTrue(isinstance(maps.get_atlas(), texturepacker.Atlas))

                    # ... and the expected recipe.
                    expected_recipe = {
                        'label': u'Foo’s bar pack 1.0 (Alt)',
                        'desc': 'Alt dog hog (2) and eel fox',
                        'parameters': {
                            'packs': ['base']},
                        'maps': 'internal:///maps/shazam',
                        'mix':  {
                            'pack': '$base',
                            'files': [
                                # XXX pack.png?
                                '*.png',
                                {
                                    'file': 'terrain.png',
                                    'replace': {
                                        'cells': {
                                            'doc_hog': 'dog_hog_2',
                                            'eel_fox': 'eel_fox_1'}}}]}}


                    # Now press the button ...
                    pack = maps.get_remix_from_code(release, code, loader=mock_loader)

                    # ...and see the machinery all work perfectly.
                    mock_add_pack.assert_called_once_with_args('base', 'JUMP')
                    mock_make.assert_called_once_with_args(expected_recipe, None)

                    self.assertEqual('THE PACK', pack)