"""
This file demonstrates two different styles of tests (one doctest and one
unittest). These will both pass when you run "manage.py test".

Replace these with more appropriate tests for your application.
"""

from django.test import TestCase
from texturejam.hello.models import *

class SimpleTest(TestCase):
    def test_default_userpic(self):
        u = User(username='foo', is_staff=True)
        u.save()
        p = u.get_profile()
        s = p.get_picture_src()
        self.assertEqual('userpic.png', s[-11:])