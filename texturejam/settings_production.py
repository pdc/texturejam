# Django settings for texturejam project.

import sys
import os
from django.template.defaultfilters import slugify

PROJECT_ROOT = os.path.dirname(__file__)
def loc(partial_path):
    return os.path.join(PROJECT_ROOT, partial_path)

DEBUG = False
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    # ('Your Name', 'your_email@domain.com'),
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'texturejam',                      # Or path to database file if using sqlite3.
        'USER': 'texturejam',                      # Not used with sqlite3.
        'PASSWORD': 'brU9USa8',                  # Not used with sqlite3.
        'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
    }
}

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'Europe/London'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-GB'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = False

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale
USE_L10N = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = loc('uploads')

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = 'http://localhost/~pdc/texturejam-uploads/'

# Where to find CSS, JavaScript etc.
STATIC_URL = 'http://static.texturejam.org.uk/'
# Directory where these files are collected
STATIC_ROOT = '/home/texturejam/static'


#
# django-social-auth configuration
#
# https://github.com/omab/django-social-auth#readme
#

AUTHENTICATION_BACKENDS = (
    'social_auth.backends.twitter.TwitterBackend',
    'social_auth.backends.facebook.FacebookBackend',
    'social_auth.backends.google.GoogleOAuthBackend',
    'social_auth.backends.google.GoogleBackend',
    'social_auth.backends.yahoo.YahooBackend',
    'social_auth.backends.contrib.livejournal.LiveJournalBackend',
    'social_auth.backends.contrib.orkut.OrkutBackend',
    'social_auth.backends.OpenIDBackend',
    'django.contrib.auth.backends.ModelBackend',
)

AUTH_PROFILE_MODULE = 'hello.Profile'

TWITTER_CONSUMER_KEY     = 'MfXykJ8fGEkuPoWR8geIDw'
TWITTER_CONSUMER_SECRET  = 'OvzsOjPTVGLbWhgshlSBquzRH9c88sDCA1eJfZxzFU'
FACEBOOK_APP_ID          = ''
FACEBOOK_API_SECRET      = ''
ORKUT_CONSUMER_KEY       = ''
ORKUT_CONSUMER_SECRET    = ''
GOOGLE_CONSUMER_KEY      = ''
GOOGLE_CONSUMER_SECRET   = ''

LOGIN_URL          = '/hello/please-log-in'
LOGIN_REDIRECT_URL = '/hello/welcome'
LOGIN_ERROR_URL    = '/hello/oh-dear'
LOGOUT_URL = '/hello/log-out'

SOCIAL_AUTH_ERROR_KEY = 'social_errors'

SOCIAL_AUTH_COMPLETE_URL_NAME  = 'complete'
SOCIAL_AUTH_ASSOCIATE_URL_NAME = 'associate_complete'

SOCIAL_AUTH_DEFAULT_USERNAME = 'crafter'
SOCIAL_AUTH_USERNAME_FIXER = lambda u: slugify(u)

SOCIAL_AUTH_EXTRA_DATA = True
SOCIAL_AUTH_EXPIRATION = 'expires'

###

HTTPLIB2_CACHE_DIR = '/home/texturejam/caches/httplib2'
RECIPES_SOURCE_PACKS_DIR = '/home/texturejam/caches/source_packs'
CACHE_BACKEND = 'file:///home/texturejam/caches/texturejam/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = '!caqtio)r6e$^)s(t7a4du=-e9@!6zb9^l$1l_crp)!z08!n6v'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)


TEMPLATE_CONTEXT_PROCESSORS = (
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.contrib.messages.context_processors.messages",
    'texturejam.hello.context_processors.profile',
    'texturejam.shortcuts.static_context_processor',
    'texturejam.shortcuts.redirect_field_value_context_processor',
)


MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
)

ROOT_URLCONF = 'texturejam.urls'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)



INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions', # Required for auth
    #'django.contrib.sites',
    'django.contrib.messages',
    # Uncomment the next line to enable the admin:
    'django.contrib.admin',
    # Uncomment the next line to enable admin documentation:
    # 'django.contrib.admindocs',
    'django.contrib.markup',
    'django.contrib.staticfiles',

    'social_auth',
    'south',

    'texturejam.hello',
    'texturejam.recipes',
    'texturejam.api',
)
