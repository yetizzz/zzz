from django.conf.urls import patterns, include, url
from django.views.generic.simple import direct_to_template
from django.conf import settings

urlpatterns = patterns('',
    url(r'^$', direct_to_template, {'template': 'base.html'}, name='home'),
    url(r'^_admin/', direct_to_template, {'template': 'admin.html'}, name='admin'),
    url(r'^api/', include('hydra.urls')),
)

if settings.DEBUG:
    urlpatterns += patterns('',
        url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {
            'document_root': settings.MEDIA_ROOT}),
    )

