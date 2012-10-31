# Coding: UTF-8

from django.test import TestCase
from django.test.client import Client
from mock import patch

import json
from textwrap import dedent
from texturejam.recipes.models import *
from django.contrib.auth.models import User

class TestApiIndex(TestCase):
    def test_api_index(self):
        resp = Client().get('/api/')
        self.assertEqual(200, resp.status_code)
        self.assertEqual('application/json', resp['Content-Type'])

        data = json.loads(resp.content)
        self.assertTrue(isinstance(data['urls']['spec_by_name'], basestring))
        self.assertTrue('{name}' in data['urls']['spec_by_name'])
        self.assertTrue('{type}' in data['urls']['spec_by_name'])

def resolve_path_template(base, template, *args, **kwargs):
    path = template.format(*args, **kwargs)
    if not path.startswith('/'):
        path = base + path
    return path

class TestGetSpec(TestCase):
    def setUp(self):
        self.owner = User.objects.create(username='OWNER')
        self.data0 = json.dumps({'hello': 'world'})
        self.spec0 = Spec(name='zero', label='Zero', spec_type='tprx', spec=self.data0, owner=self.owner)
        self.spec0.save()
        self.data1 = json.dumps({'banjo': 'ukelele'})
        self.spec1 = Spec(name='wan', label='Wan maps', spec_type='tpmaps', spec=self.data1, owner=self.owner)
        self.spec1.save()

        self.index = json.loads(Client().get('/api/').content)

    def get_spec_path(self, name, type):
        return resolve_path_template('/api/', self.index['urls']['spec_by_name'], name=name, type=type)

    def get_spec_edit_path(self, name, type):
        info = json.loads(Client().get(self.get_spec_path(name, type)).content)
        info['edit']

    def test_get_spec_info(self):
        resp = Client().get(self.get_spec_path('zero', 'tprx'))
        self.assertEqual(200, resp.status_code)
        self.assertEqual('application/json', resp['Content-Type'])

        data = json.loads(resp.content)
        self.assertEqual('/rx/zero', data['pub'])
        self.assertTrue(data['edit'])

        self.assertEqual('Zero', data['label'])

    def test_get_spec_info_maps(self):
        resp = Client().get(self.get_spec_path('wan', 'tpmaps'))
        self.assertEqual(200, resp.status_code)
        self.assertEqual('application/json', resp['Content-Type'])

        data = json.loads(resp.content)
        self.assertEqual('/rx/maps/wan', data['pub'])
        self.assertTrue(data['edit'])

        self.assertEqual('Wan maps', data['label'])

    def test_has_etag(self):
        # Tests whether getting the raw data includes the ETag.
        resp0 = Client().get('/rx/zero')
        self.assertEqual(200, resp0.status_code)
        self.assertEqual(self.data0, resp0.content) # Obviously

        resp1 = Client().get('/rx/maps/wan')
        self.assertEqual(200, resp1.status_code)
        self.assertEqual(self.data1, resp1.content)

        self.assertTrue(resp0['ETag'])
        self.assertTrue(resp1['ETag'])
        self.assertNotEqual(resp0['Etag'], resp1['Etag'])

    def test_etag_is_in_spec_metadata(self):
        metadata = json.loads(Client().get(self.get_spec_path('wan', 'tpmaps')).content)
        resp2 = Client().get('/rx/maps/wan')
        self.assertEqual(resp2['ETag'], metadata['etag'])

    def xtest_needs_authentication(self):
        p = self.get_spec_edit_path('zero', 'tprx')
        data2 = '{"hello": "sailor"}'
        resp2 = Client().put(p, data2, 'application/json')
        self.assertEqual(401, resp2.status_code)
        self.assertTrue('digest' in resp['WWW-Authenticate'])

    def xtest_put_ok(self):
        p = self.get_spec_edit_path('zero', 'tprx')
        etag0 = Client().get('/api/specs/zero')['ETag']

        data2 = '{"hello": "sailor"}'
        resp2 = Client().put(p, data2, 'application/x-json', IF_MATCH=etag0)
        self.assertTrue(resp2.status_code in [200, 204])

        resp3 = Client().get('/rx/zero')
        self.assertEqual(200, resp3.status_code)
        self.assertEqual(data2, resp3.content) # It was updated!
        self.assertNotEqual(resp2['ETag'], etag0) # New etag

    def xtest_put_no_match(self):
        p = self.get_spec_edit_path('zero', 'tprx')
        etag0 = '"xerxes"'

        data2 = '{"hello": "sailor"}'
        resp2 = Client().put(p, data2, 'application/x-json', IF_MATCH=etag0)
        self.assertEqual(412, resp2.status_code)

        resp3 = Client().get('/rx/zero')
        self.assertEqual(200, resp3.status_code)
        self.assertEqual(self.data0, resp3.content) # It was NOT updated!

