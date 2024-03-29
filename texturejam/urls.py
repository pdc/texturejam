from django.conf.urls.defaults import *
from django.conf import settings

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('texturejam.recipes.views',
    (r'^$', 'remix_list', {}, 'home'),

    (r'^remixes/(?P<remix_id>\d+)/$', 'remix_detail', {}, 'remix-detail'),
    (r'^remixes/(?P<remix_id>\d+)/progress$', 'remix_progress_json', {}, 'remix-progress-json'),
    (r'^remixes/(?P<remix_id>\d+)/edit$', 'remix_edit', {}, 'remix-edit'),
    (r'^remixes/(?P<remix_id>\d+)/resources/(?P<resource_name>.*)$', 'remix_resource', {}, 'remix-resource'),
    (r'^remixes/(?P<remix_id>\d+)/(?P<slug>[\w-]+)\.zip$', 'make_texture_pack', {}, 'tpmake'),

    (r'^mixing/download-and-upgrade/(?P<task_id>\d+)/$', 'download_task_progress', {}, 'download-task-progress'),
    (r'^mixing/download-and-upgrade/(?P<task_id>\d+)/progress$', 'download_task_progress_json', {}, 'download-task-progress-json'),

    (r'^sources/$', 'source_list', {'tag_names_plusified': ''}, 'source-list'),
    (r'^sources/bytag/(?P<tag_names_plusified>[\w+-]+)$', 'source_list', {}, 'source-list'),
    (r'^sources/(?P<source_id>\d+)/$', 'source_detail', {}, 'source-detail'),
    (r'^sources/(?P<source_id>\d+)/edit$', 'source_edit', {}, 'source-edit'),
    (r'^sources/(?P<source_id>\d+)/releases/(?P<release_id>\d+)/resources/(?P<resource_name>.*)$', 'source_resource', {}, 'source-resource'),

    (r'^beta-upgrade$', 'beta_upgrade', {}, 'beta_upgrade'),
    (r'^altpacks/(?P<maps_id>\d+)$', 'recipe_from_maps', {}, 'recipe-from-maps'),
    (r'^altpacks/(?P<maps_id>\d+)/releases/(?P<release_id>\d+)/(?P<slug>[\w-]+)-(?P<code>[a-z_]+)\.zip$',
        'make_alts_pack', {}, 'make-alts-pack'),
    (r'^instant-upgrade/(?P<source_id>\d+)', 'instant_upgrade', {}, 'instant-upgrade'),

    (r'^rx/(?P<name>[\w-]+)$', 'spec', {'spec_type': 'tprx'}, 'tprx'),
    (r'^rx/maps/(?P<name>[\w-]+)$', 'spec', {'spec_type': 'tpmaps'}, 'tpmaps'),

    url(r'^api/', include('texturejam.api.urls')),
)

urlpatterns += patterns('',
    url(r'', include('social_auth.urls')),

    url(r'^hello/welcome$', 'texturejam.hello.views.logged_in'),
    url(r'^hello/oh-dear$', 'texturejam.hello.views.login_error'),
    url(r'^hello/callback$', 'texturejam.hello.views.oauth_callback'),
    url(r'^hello/log-out$', 'texturejam.hello.views.log_out', {}, 'hello_log_out'),
    url(r'^hello/please-log-in$', 'texturejam.hello.views.login_form', {}, 'hello_please_log_in'),
    url(r'^hello/test-messages$', 'texturejam.hello.views.test_messages'),

    # Uncomment the admin/doc line below to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    (r'^admin/', include(admin.site.urls)),
)

# Old URLs redirected to new ones.
urlpatterns += patterns('django.views.generic.simple',
    (r'^packs/(?P<remix_id>\d+)/$', 'redirect_to', {'url': '/remixes/%(remix_id)s/'}),
)