from django.conf.urls import patterns, include, url
from tastypie.api import Api

from hydra.api import HydraResource
from analytics.resources import VisitResource


api = Api(api_name='v1')
api.register(HydraResource())
api.register(VisitResource())


urlpatterns = patterns('',
    url(r'^', include(api.urls)),
)
