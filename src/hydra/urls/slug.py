from django.conf.urls import patterns, url
from django.views.generic import TemplateView

from hydra.views import SlugLookupRedirectView


urlpatterns = patterns('',
    url(r'^_/(?P<slug>.+)',
        TemplateView.as_view(template_name='base.html'),
        name='slug-details'),
    url(r'^(?P<slug>.+)',
        SlugLookupRedirectView.as_view(),
        name='slug-redirect'),
)
