from django.core.urlresolvers import reverse
from django.conf import settings
from django.http import HttpResponseRedirect
from django.views.generic import RedirectView, TemplateView, FormView
from analytics.models import Visit

from .api import RedisProject, RedisRedirect
from .forms import SlugForm

THRESHOLD = getattr(settings, "THRESHOLD", 3)

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
        if urls and urls[0]['score'] > THRESHOLD:
            if len(urls) > 1:
                if urls[0]['score'] - urls[1]['score'] > THRESHOLD:
                    redirect_url = urls[0]['url']
            else:
                redirect_url = urls[0]['url']
        if not redirect_url:
            Visit.objects.create(
                project=project,
                slug=slug,
                retval=', '.join([url['url'] for url in urls]))
            return reverse('slug-details', kwargs={'slug': slug,
                                                   'project': project})

        Visit.objects.create(project=project, slug=slug, retval=redirect_url)
        return redirect_url


class SlugDetailView(FormView):
    form_class = SlugForm

    def get_context_data(self, *args, **kwargs):
        slug = self.kwargs.get('slug', '')
        project = self.kwargs.get('project', '')
        context = super(SlugDetailView, self).get_context_data(*args, **kwargs)
        context.update(self.kwargs)
        proj_obj = RedisRedirect(slug=slug, project=project)
        urls = proj_obj.get_urls()
        if urls and urls[0]['score'] > THRESHOLD:
            context['winner'] = urls[0]['url']
        context['urls'] = urls
        context['THRESHOLD'] = THRESHOLD
        context.update(self.kwargs)
        return context

    def get_success_url(self, *args, **kwargs):
        slug = self.kwargs.get('slug', '')
        project = self.kwargs.get('project', '')
        url = self.request.POST['url']
        redirect = RedisRedirect(slug=slug,
                                 project=project)
        redirect.incr(url)
        return url


class ProjectView(TemplateView):
    extra_context = None

    def get_context_data(self, *args, **kwargs):
        context = super(ProjectView, self).get_context_data(*args, **kwargs)
        context['projects'] = RedisProject.all_projects()
        selected_proj = self.request.GET.get('project', None)
        if selected_proj:
            context['selected_project'] = selected_proj
        context.update(kwargs)
        return context

    def post(self, request, *args, **kwargs):
        if request.method == 'POST':
            url = reverse('slug-details', kwargs={
                'project': request.POST.get('project'),
                'slug': request.POST.get('q'),
            })
            return HttpResponseRedirect(url)

        return super(ProjectView, self).post(request, *args, **kwargs) 


class ProjectRedirect(RedirectView):
    permanent = False

    def get_redirect_url(self, **kwargs):
        project = kwargs.get('project', '')
        return "%s?project=%s" % (reverse("search"), project)
