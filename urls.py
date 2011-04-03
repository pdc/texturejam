from django.conf.urls.defaults import *
from django.conf import settings

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('recipes.views',
    (r'^$', 'remix_list', {}, 'home'),

    (r'^remixes/(?P<pk>\d+)/$', 'remix_detail', {}, 'remix-detail'),
    (r'^remixes/(?P<pk>\d+)/cooking$', 'remix_cooking', {}, 'remix-cooking'),
    (r'^remixes/(?P<pk>\d+)/progress$', 'remix_progress', {}, 'remix-progress'),
    (r'^remixes/(?P<pk>\d+)/edit$', 'remix_edit', {}, 'remix-edit'),
    (r'^remixes/(?P<pk>\d+)/resources/(?P<res_name>.*)$', 'remix_resource', {}, 'remix-resource'),
    (r'^remixes/(?P<pk>\d+)/(?P<slug>[\w-]+)\.zip$', 'make_texture_pack', {}, 'tpmake'),

    (r'^sources/(?P<pk>\d+)/$', 'source_detail', {}, 'source-detail'),
    (r'^sources/(?P<pk>\d+)/edit$', 'source_edit', {}, 'source-edit'),
    (r'^sources/(?P<pk>\d+)/releases/(?P<release_pk>\d+)/resources/(?P<res_name>.*)$', 'source_resource', {}, 'source-resource'),

    (r'^beta-upgrade$', 'beta_upgrade', {}, 'beta_upgrade'),
    (r'^recipe-from-maps/(?P<id>\d+)', 'recipe_from_maps', {}, 'recipe-from-maps'),

    (r'^rx/(?P<name>[\w-]+)/$', 'recipe', {}, 'tprx'),
    (r'^rx/maps/(?P<name>[\w-]+)$', 'maps', {}, 'tpmaps'),
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
    (r'^packs/(?P<pk>\d+)/$', 'redirect_to', {'url': '/remixes/%(pk)s/'}),
)