from django.conf.urls import patterns, include, url
from django.views.generic import TemplateView

from hydra.views import SlugLookupRedirectView


urlpatterns = patterns('',
    url(r'^_/(?P<slug>[-\w\d]+)',
        TemplateView.as_view(template_name='base.html'),
        name='slug-details'),
    url(r'^(?P<slug>[-\w\d]+)',
        SlugLookupRedirectView.as_view(),
        name='slug-redirect'),
)
