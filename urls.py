from django.conf.urls.defaults import *
from django.conf import settings

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('recipes.views',
    (r'^$', 'remix_list', {}, 'home'),

    (r'^remixes/(?P<remix_id>\d+)/$', 'remix_detail', {}, 'remix-detail'),
    (r'^remixes/(?P<remix_id>\d+)/edit$', 'remix_edit', {}, 'remix-edit'),
    (r'^remixes/(?P<remix_id>\d+)/resources/(?P<resource_name>.*)$', 'remix_resource', {}, 'remix-resource'),
    (r'^remixes/(?P<remix_id>\d+)/(?P<slug>[\w-]+)\.zip$', 'make_texture_pack', {}, 'tpmake'),

    (r'^mixing/(?P<task_id>\d+)/$', 'remix_cooking', {}, 'remix-cooking'),
    (r'^mixing/(?P<task_id>\d+)/progress$', 'remix_progress', {}, 'remix-progress'),

    (r'^sources/$', 'source_list', {'tag_names_plusified': ''}, 'source-list'),
    (r'^sources/bytag/(?P<tag_names_plusified>[\w+-]+)$', 'source_list', {}, 'source-list'),
    (r'^sources/(?P<source_id>\d+)/$', 'source_detail', {}, 'source-detail'),
    (r'^sources/(?P<source_id>\d+)/edit$', 'source_edit', {}, 'source-edit'),
    (r'^sources/(?P<source_id>\d+)/releases/(?P<release_id>\d+)/resources/(?P<resource_name>.*)$', 'source_resource', {}, 'source-resource'),

    (r'^beta-upgrade$', 'beta_upgrade', {}, 'beta_upgrade'),
    (r'^recipe-from-maps/(?P<id>\d+)', 'recipe_from_maps', {}, 'recipe-from-maps'),

    (r'^rx/(?P<name>[\w-]+)$', 'spec', {'spec_type': 'tprx'}, 'tprx'),
    (r'^rx/maps/(?P<name>[\w-]+)$', 'spec', {'spec_type': 'tpmaps'}, 'tpmaps'),

    url(r'^api/', include('api.urls')),
)

urlpatterns += patterns('',
    url(r'', include('social_auth.urls')),

    url(r'^hello/welcome$', 'hello.views.logged_in'),
    url(r'^hello/oh-dear$', 'hello.views.login_error'),
    url(r'^hello/callback$', 'hello.views.oauth_callback'),
    url(r'^hello/log-out$', 'hello.views.log_out', {}, 'hello_log_out'),
    url(r'^hello/please-log-in$', 'hello.views.login_form', {}, 'hello_please_log_in'),
    url(r'^hello/test-messages$', 'hello.views.test_messages'),

    # Uncomment the admin/doc line below to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    (r'^admin/', include(admin.site.urls)),
)

# Old URLs redirected to new ones.
urlpatterns += patterns('django.views.generic.simple',
    (r'^packs/(?P<remix_id>\d+)/$', 'redirect_to', {'url': '/remixes/%(remix_id)s/'}),
)