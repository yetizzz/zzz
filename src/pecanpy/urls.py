from django.conf.urls import patterns, url
from django.utils.functional import curry
from django.core.urlresolvers import reverse
from django.views.generic import TemplateView

class PecanView(TemplateView):
    def get_context_data(self, *args, **kwargs):
        base = super(PecanView, self).get_context_data(*args, **kwargs) or {}
        base.update({'base_url': curry(reverse, 'pecanpy_root')})
        return base

urlpatterns = patterns('',
    url(r'^',
        PecanView.as_view(template_name='pecanpy/index.html'),
        name='pecanpy_root')
)
