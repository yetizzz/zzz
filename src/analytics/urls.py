from django.conf.urls import patterns, include, url
from tastypie.api import Api

from analytics.resources import VisitResource


api = Api(api_name='v1')
api.register(VisitResource())


urlpatterns = patterns('',
    (r'^', include(api.urls)),
)
