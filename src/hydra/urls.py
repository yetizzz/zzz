from django.conf.urls import patterns, include, url
from django.views.generic.simple import direct_to_template

from hydra.api import HydraResource

hydra_resource = HydraResource()

urlpatterns = patterns('',
    (r'^api/', include(hydra_resource.urls)),
)
