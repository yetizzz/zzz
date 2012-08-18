from django.core.urlresolvers import reverse
from django.views.generic import RedirectView

from .api import get_urls


class SlugLookupRedirectView(RedirectView):
    permanent = False

    def get_redirect_url(self, **kwargs):
        slug = kwargs.get('slug', '')
        if slug == '':
            return reverse('home')
        urls = get_urls(slug, count=1)
        if not urls:
            return reverse('slug-details', kwargs={'slug': slug})

        return urls[0]['url']
