from django.conf.urls import patterns, include, url
from tastypie.api import Api

from hydra.api import RedirectResource, ProjectResource
from analytics.resources import VisitResource

api = Api(api_name='v1')
api.register(RedirectResource())
api.register(ProjectResource())
api.register(VisitResource())

urlpatterns = patterns('',
    url(r'^', include(api.urls)),
)
