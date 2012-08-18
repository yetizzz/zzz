from django.conf.urls import patterns, include, url
from django.views.generic.simple import TemplateView
from django.conf import settings

urlpatterns = patterns('',
    url(r'^$', TemplateView.as_view(template='base.html'), name='home'),
    url(r'^_admin/', TemplateView.as_view(template='admin.html'), name='admin'),
    url(r'^api/', include('hydra.urls')),
)


if settings.DEBUG:
    urlpatterns += patterns('',
        url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {
            'document_root': settings.MEDIA_ROOT}),
    )
