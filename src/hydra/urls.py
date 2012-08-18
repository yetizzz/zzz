from django.conf.urls import patterns, include, url
from django.views.generic.simple import direct_to_template
from tastypie.api import Api 

from hydra.api import HydraResource

api = Api(api_name='v1')

api.register(HydraResource())

urlpatterns = patterns('',
    (r'^', include(api.urls)),
)
