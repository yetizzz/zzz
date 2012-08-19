from django.conf.urls import patterns, url
from django.views.generic import TemplateView

from hydra.views import SlugLookupRedirectView, SlugDetailView


urlpatterns = patterns('',
    url(r'^_/(?P<slug>.+)',
        SlugDetailView.as_view(template_name='slug-details.html'),
        name='slug-details'),
    url(r'^(?P<slug>.+)',
        SlugLookupRedirectView.as_view(),
        name='slug-redirect'),
)
