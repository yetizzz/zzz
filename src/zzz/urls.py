from django.conf.urls import patterns, include, url
from django.views.generic import TemplateView
from django.conf import settings


urlpatterns = patterns('',
    url(r'^$',
        TemplateView.as_view(template_name='base.html'),
        name='home'),
    url(r'^_admin/',
        TemplateView.as_view(template_name='admin.html'),
        name='admin'),
    url(r'^api/', include('hydra.urls')),
)


if settings.DEBUG:
    urlpatterns += patterns('',
        url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {
            'document_root': settings.MEDIA_ROOT}),
    )
