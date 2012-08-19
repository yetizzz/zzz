from django.core.urlresolvers import reverse
from django.views.generic import RedirectView, TemplateView
from analytics.models import Visit
from .utils import get_urls


class SlugLookupRedirectView(RedirectView):
    permanent = False

    def get_redirect_url(self, **kwargs):
        slug = kwargs.get('slug', '')
        if slug == '':
            return reverse('home')

        redirect_url = ''
        urls = get_urls(slug)
        if urls and urls[0]['score'] > 5:
            if len(urls) > 1:
                if urls[0]['score'] - urls[1]['score'] > 5:
                    redirect_url = urls[0]['url']
        if not redirect_url:
            Visit.objects.create(key=slug,
                                 retval=', '.join([url['url'] for url in urls]))
            return reverse('slug-details', kwargs={'slug': slug})

        Visit.objects.create(key=slug, retval=redirect_url)
        return redirect_url


class SlugDetailView(TemplateView):
    extra_context = None

    def get_context_data(self, *args, **kwargs):
        context = super(SlugDetailView, self).get_context_data(*args, **kwargs)
        context.update(kwargs)
        context['urls'] = get_urls(kwargs['slug'])
        return context
