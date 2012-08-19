from django.core.urlresolvers import reverse
from django.views.generic import RedirectView, FormView, TemplateView

from analytics.models import Visit

from .api import RedisProject, RedisRedirect
from .forms import SlugForm


class SlugLookupRedirectView(RedirectView):
    permanent = False

    def get_redirect_url(self, **kwargs):
        slug = kwargs.get('slug', '')
        project = kwargs.get('project', '')
        if slug == '':
            return reverse('home')

        redirect_url = ''
        proj_obj = RedisRedirect(slug=slug, project=project)
        urls = proj_obj.get_urls()
        if urls and urls[0]['score'] > 5:
            if len(urls) > 1:
                if urls[0]['score'] - urls[1]['score'] > 5:
                    redirect_url = urls[0]['url']
        if not redirect_url:
            Visit.objects.create(key=slug,
                                 retval=', '.join([url['url'] for url in urls]))
            return reverse('slug-details', kwargs={'slug': slug,
                                                   'project': project})

        Visit.objects.create(key=slug, retval=redirect_url)
        return redirect_url


class SlugDetailView(FormView):
    form_class = SlugForm

    def get_context_data(self, *args, **kwargs):
        slug = kwargs.get('slug', '')
        project = kwargs.get('project', '')
        context = super(SlugDetailView, self).get_context_data(*args, **kwargs)
        proj_obj = RedisRedirect(slug=slug, project=project)
        context['urls'] = proj_obj.get_urls()
        context['slug'] = self.kwargs['slug']
        return context

    def get_success_url(self, *args, **kwargs):
        return self.request.POST['url']


class HomeView(TemplateView):
    extra_context = None

    def get_context_data(self, *args, **kwargs):
        context = super(HomeView, self).get_context_data(*args, **kwargs)
        context['projects'] = RedisProject.all_projects()
        return context
