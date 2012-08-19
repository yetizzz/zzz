from django.conf.urls import patterns, include, url
from django.views.generic import TemplateView
from django.conf import settings

from hydra.views import ProjectView


urlpatterns = patterns('',
    url(r'^$',
        ProjectView.as_view(template_name='home.html'),
        name='home'),
)

if settings.DEBUG:
    urlpatterns += patterns('',
        url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {
            'document_root': settings.MEDIA_ROOT}),
    )

urlpatterns += patterns('',
    url(r'^_admin/',
        include('pecanpy.urls')),
    url(r'^_search/',
        ProjectView.as_view(template_name='search.html'),
        name='search'),
    url(r'^_api/', include('hydra.urls.api')),
    url(r'^', include('hydra.urls.slug')),
)
