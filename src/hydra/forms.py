from django import forms


class SlugForm(forms.Form):
    slug = forms.CharField(max_length=255)
    url = forms.URLField()
