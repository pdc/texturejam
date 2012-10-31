from django.conf.urls.defaults import *
from django.conf import settings

urlpatterns = patterns('texturejam.api.views',
    (r'^$', 'index_page', {}, 'api_index'),
    (r'specs/(?P<type>\w+)/(?P<name>[\w-]+)', 'spec_page', {}, 'api_spec'),
)