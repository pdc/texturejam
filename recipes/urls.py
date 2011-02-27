from django.conf.urls.defaults import *

urlpatterns = patterns('recipes.views',
    (r'^$', 'recipe_pack_list'),
)
