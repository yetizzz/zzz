from django import forms

from .api import RedisProject
from .utils import in_whitelist

class SlugForm(forms.Form):
    project = forms.CharField(max_length=255)
    slug = forms.CharField(max_length=255)
    url = forms.URLField()

    def clean_url(self):
        url = self.cleaned_data['url']
        project = self.cleaned_data['project']
        valid, msg = in_whitelist(project, url)
        if not valid:
            raise forms.ValidationError(msg)
        return url
