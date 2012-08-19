from django.conf.urls import patterns, url

from hydra.views import SlugLookupRedirectView, SlugDetailView, ProjectRedirect


urlpatterns = patterns('',
    url(r'^_/(?P<project>[^/]+)/(?P<slug>[^/]+)',
        SlugDetailView.as_view(template_name='slug-details.html'),
        name='slug-details'),
    url(r'^(?P<project>[^/]+)/(?P<slug>[^/]+)',
        SlugLookupRedirectView.as_view(),
        name='slug-redirect'),
    url(r'^(?P<project>[^/]+)/',
        ProjectRedirect.as_view(),
        name='project-redirect'),
)
