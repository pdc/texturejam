from django.conf.urls.defaults import *
from django.conf import settings

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('recipes.views',
    (r'^$', 'recipe_pack_list', {}, 'home'),
    (r'^beta-upgrade$', 'beta_upgrade', {}, 'beta_upgrade'),

    (r'^rx/(?P<name>[\w-]+)$', 'recipe', {}, 'tprx'),
    (r'^rx/maps/(?P<name>[\w-]+)$', 'maps', {}, 'tpmaps'),
    (r'^tp/(?P<pk>\d+)$', 'make_texture_pack', {}, 'tpmake'),
)

urlpatterns += patterns('',
    url(r'', include('social_auth.urls')),

    url(r'^hello/welcome$', 'hello.views.logged_in'),
    url(r'^hello/oh-dear$', 'hello.views.login_error'),
    url(r'^hello/callback$', 'hello.views.oauth_callback'),
    url(r'^hello/log-out$', 'hello.views.log_out', {}, 'hello_log_out'),

    # Uncomment the admin/doc line below to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    (r'^admin/', include(admin.site.urls)),
)
