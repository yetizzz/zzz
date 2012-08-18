from django.conf.urls import patterns, include, url
from tastypie.api import Api

from hydra.api import HydraResource


api = Api(api_name='v1')
api.register(HydraResource())


urlpatterns = patterns('',
    url(r'^', include(api.urls)),
)
