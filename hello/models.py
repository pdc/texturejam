# -*-coding: UTF-8-*-

import json
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.conf import settings
from social_auth.models import UserSocialAuth
from social_auth.signals import pre_update
from social_auth.backends.twitter import TwitterBackend
from texturejam.shortcuts import get_http

class Profile(models.Model):
    """Additional information about logged-in user."""
    user = models.OneToOneField(User)

    pic_src = models.URLField(blank=True, help_text='URL of a profile picture for this user.')
    minecraft_name = models.CharField(max_length=200, blank=True)
    forum_name = models.CharField(max_length=200, blank=True)

    def get_picture_src(self):
        if not self.pic_src and self.user.is_authenticated():
            try:
                social_auth = self.user.social_auth.get()
                func_name = 'get_{provider}_pic'.format(provider=social_auth.provider)
                func = getattr(self, func_name)
                if func:
                    self.pic_src = func()
                    self.save()
            except UserSocialAuth.DoesNotExist:
                pass

        return self.pic_src or (settings.STATIC_URL + 'style/userpic.png')

    def get_twitter_pic(self):
        social_auth = self.user.social_auth.get()
        u = 'http://api.twitter.com/1/users/show/{uid}.json'.format(uid=social_auth.uid)
        response, body = get_http().request(u)
        if response.status in (200, 304):
            prof = json.loads(body)
            return prof['profile_image_url']

def create_profile_if_missing(user):
    """Given a user object, return that user’s profile.

    Creates it if it does not already exist."""
    try:
        return user.get_profile()
    except Profile.DoesNotExist:
        profile = Profile(user=user)
        profile.save()
        return profile


# Hook in to the signal system to create user profile when user created.

def on_post_save_user(sender, instance, created, **kwargs):
    if created or not instance.get_profile():
        Profile(user=instance).save()

post_save.connect(on_post_save_user, User)