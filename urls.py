from django.conf.urls.defaults import *
from django.conf import settings

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('recipes.views',
    (r'^$', 'recipe_pack_list', {}, 'home'),
    (r'^packs/(?P<pk>\d+)/$', 'recipe_pack_detail', {}, 'pack'),
    (r'^packs/(?P<pk>\d+)/resources/(?P<res_name>.*)$', 'recipe_pack_resource', {}, 'pack_resource'),
    (r'^packs/(?P<pk>\d+)/zip$', 'make_texture_pack', {}, 'tpmake'),

    (r'^beta-upgrade$', 'beta_upgrade', {}, 'beta_upgrade'),
    (r'^its-cooking/(?P<pk>\d+)$', 'its_cooking', {}, 'its_cooking'),

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
