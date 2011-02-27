from django.conf.urls.defaults import *

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('recipes.views',
    (r'^$', 'recipe_pack_list'),
    (r'^rx/(?P<name>[\w-]+)$', 'recipe', {}, 'tprx'),
    (r'^rx/maps/(?P<name>[\w-]+)$', 'maps', {}, 'tpmaps'),
    (r'^tp/(?P<pk>\d+)$', 'make_texture_pack', {}, 'tpmake'),
)

urlpatterns += patterns('',
    # Uncomment the admin/doc line below to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    (r'^admin/', include(admin.site.urls)),
)
