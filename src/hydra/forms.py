from urlparse import urlparse

from django import forms

from .api import RedisProject


class SlugForm(forms.Form):
    project = forms.CharField(max_length=255)
    slug = forms.CharField(max_length=255)
    url = forms.URLField()

    def clean_url(self):
        url = self.cleaned_data['url']
        parsed_url = urlparse(url)
        if parsed_url.scheme == '':
            raise forms.ValidationError('url must be absolute')
        project = RedisProject(self.cleaned_data['project'])
        if not any([parsed_url.netloc.endswith(domain)
                    for domain in project.whitelist]):
            raise forms.ValidationError('url is not on a whitelisted domain')
        return url
