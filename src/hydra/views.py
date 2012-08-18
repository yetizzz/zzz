from django.core.urlresolvers import reverse
from django.views.generic.simple import RedirectView

from .api import make_key, r


class RedisLookupRedirectView(RedirectView):
    permanent = False

    def get_redirect_url(**kwargs):
        slug = kwargs.get('slug', '')
        if slug == '':
            reverse('top-urls')
        url = r.get(make_key(slug))
        return url
