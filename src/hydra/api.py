"""
A redis-based Tastypie API.

It adds has "Model" type objects RedisProject and RedisRedirect. These are used
for all of the data access, and for hydration at the Tastypie level.

Then we have resources that are based on these models. The ProjectResource and
RedirectResource map onto the model objects listed above.

This could be a generic interface, and the code is most of the way there to
making a moderately generic BaseResource for interacting with Redis Models.
"""
import redis

from django.conf.urls import url
from django.conf import settings

from tastypie.resources import Resource
from tastypie import fields
from tastypie.authorization import Authorization, DjangoAuthorization
from tastypie.authentication import Authentication, BasicAuthentication
from tastypie.exceptions import NotFound, ImmediateHttpResponse
from tastypie.http import HttpConflict
from tastypie.validation import Validation


r = redis.StrictRedis.from_url(settings.REDIS_URL)


class RedisProject(object):
    """
    A model layer representing a Project in Redis.

    It has an index of all existing projects, and then contains metadata about
    projects including their existence, and a whitelist of URLs that you can
    link to from them.

    Generally you create an instance by passing in a name, and a possible
    whitelist. If you only pass in the name, the whitelist is populated from
    the data store.

    The main methods you will call on an instance are save, delete, and exists.
    There is a classmethod called all_projects that will return all projects.

    """
    index_slug = "hydra:v1:projects"

    def __init__(self, name=None, whitelist=None, *args, **kwargs):
        super(RedisProject, self).__init__(*args, **kwargs)
        self.name = name
        if whitelist:
            self.whitelist = whitelist
        else:
            # We need to populate the whitelist here,
            # so when we return the object, it will serialize with them
            self.whitelist = self.get_whitelist()

    @classmethod
    def all_projects(cls):
        """
        Return all projects. Classmethod because it doesn't need any data on
        the instance.
        """
        ret_val = r.sort(cls.index_slug)
        return ret_val

    @property
    def redis_slug(self):
        return "hydra:v1:projects:%s" % (self.name)

    def save_whitelist(self):
        for url in self.whitelist:
            r.sadd("%s:whitelist" % self.redis_slug, url)

    def save_project(self):
        r.hset(self.redis_slug, "exists", "true")
        r.sadd(self.index_slug, self.name)

    def save(self):
        self.save_whitelist()
        self.save_project()

    def delete(self):
        r.delete(self.redis_slug)
        r.delete("%s:whitelist" % self.redis_slug)
        r.srem(self.index_slug, self.name)

    def exists(self):
        return r.hget(self.redis_slug, "exists") == "true"

    def get_whitelist(self):
        return r.smembers("%s:whitelist" % self.redis_slug)

class ProjectResource(Resource):
    """
    A Resource representing a Project.

    Provides GET, POST, PUT, DELETE. See the README for more details.

    name - The name of the project
    whitelist - Sites that links are allowed to go to.
    """

    name = fields.CharField(attribute='name')
    whitelist = fields.ListField(attribute="whitelist")

    class Meta:
        main_ident = "name"
        resource_name = "project"
        object_class = RedisProject
        authorization = Authorization()
        authentication = Authentication()

    def get_resource_uri(self, bundle_or_obj):
        try:
            if getattr(bundle_or_obj, 'obj'):
                return "/_api/v1/project/%s/" % bundle_or_obj.obj.name
            return "/_api/v1/project/%s/" % bundle_or_obj.name
        except:
            return ""

    def obj_create(self, bundle, request=None, **kwargs):
        bundle.obj = RedisProject(**bundle.data)
        bundle = self.full_hydrate(bundle)
        if kwargs.get('delete', None):
            bundle.obj.delete()
        bundle.obj.save()
        return bundle

    def obj_update(self, bundle, request=None, **kwargs):
        if bundle.data.get('resource_uri'):
            del bundle.data['resource_uri']
        return self.obj_create(bundle, request, delete=True, **kwargs)

    def obj_get(self, request=None, pk=None, **kwargs):
        proj = RedisProject(pk)
        if not proj.exists():
            raise NotFound("No object matching this pk")
        return proj

    def obj_get_list(self, request=None, **kwargs):
        ret_val = []
        filter_slug = request.GET.get('slug', None)
        if not filter_slug:
            filter_slug = request.GET.get('q', None)
        keys = RedisProject.all_projects()
        for key in keys:
            #filter
            if not filter_slug or filter_slug in key:
                obj = RedisProject(name=key)
                ret_val.append(obj)
        return ret_val

    def obj_delete(self, request=None, **kwargs):
        obj = RedisProject(kwargs['pk'])
        obj.delete()

    def obj_delete_list(self, request=None, **kwargs):
        for name in RedisProject.all_projects():
            obj = RedisProject(name)
            obj.delete()

    def override_urls(self):
        raw_url = r"^(?P<resource_name>%s)/(?P<pk>.+)/$"
        return [
            url(r"^(?P<resource_name>%s)/schema/$" % self._meta.resource_name,
                self.wrap_view('get_schema'),
                name="api_get_schema"),
            url(raw_url % self._meta.resource_name,
                self.wrap_view('dispatch_detail'),
                name="api_dispatch_detail"),
        ]

class RedisRedirect(object):
    """
    A Redis Model for a Redirect

    This contains the basic information about how a projects redirects will
    work.

    The set of (project, slug) is unique, and each contains a set of URLs that
    might possibly be correct. We store these in a sorted set so that we can
    keep score of clicks in the data model in Redis.
    """

    def __init__(self, slug=None, project=None, urls=None, *args, **kwargs):
        super(RedisRedirect, self).__init__(*args, **kwargs)
        self.project = project
        self.slug = slug
        if urls:
            self.urls = urls
        else:
            self.urls = self.get_urls()

    @property
    def index_slug(self):
        return "hydra:v1:projects:%s:slugs" % (self.project)

    @property
    def redis_slug(self):
        return "%s:%s" % (self.index_slug, self.slug)

    def all_slugs(self):
        return r.sort(self.index_slug)

    def save_redirect(self):
        r.sadd(self.index_slug, self.slug)

    def save_urls(self):
        for obj in self.urls:
            if hasattr(obj, 'get'):
                if obj.get('score', None):
                    r.zadd(self.redis_slug, int(obj['score']), obj['url'])
            else:
                r.zincrby(self.redis_slug, self.urls[0], 1)

    def save(self):
        proj = RedisProject(name=self.project)
        proj.save()
        self.save_redirect()
        self.save_urls()
        return True

    def delete(self):
        r.delete(self.redis_slug)
        r.srem(self.index_slug, self.slug)

    def incr(self, url):
        self.save_redirect()
        r.zincrby(self.redis_slug, url, 1)

    def url_exists(self, url):
        for url_obj in self.get_urls():
            if url == url_obj['url']:
                return True
        return False

    def exists(self):
        return r.zcard(self.redis_slug)

    def get_urls(self):
        urls = r.zrevrange(self.redis_slug, 0, -1, withscores=True)
        ret_val = []
        for obj in urls:
            redirect_url, score = obj
            ret_val.append({
                'score': score,
                'url': redirect_url
            })
        return ret_val


class URLValidation(Validation):
    def is_valid(self, bundle, request=None):
        if not bundle.data:
            return {'__all__': 'No data provided.'}
        errors = {}

        if not 'project' in bundle.data:
            errors['project'] = 'required field'
        if not 'slug' in bundle.data:
            errors['slug'] = 'required field'
        if not 'urls' in bundle.data:
            errors['urls'] = 'required field'

        if not errors:
            from .utils import in_whitelist
            for url in bundle.data['urls']:
                valid, msg = in_whitelist(bundle.data['project'], url['url'])
                if not valid:
                    errors['urls'] = errors.get('urls', '') + msg

        return errors


class RedirectResource(Resource):
    """
    A tastypie Resource that maps to the Redirect Redis Model

    slug - The URL slug that will identify this Redirect
    project - The project the slug belongs to
    urls - The Sorted Set of URLs. We use score to keep track of clicks on
           the Redirects.
    """
    slug = fields.CharField(attribute='slug')
    project = fields.CharField(attribute='project')
    urls = fields.ListField(attribute='urls', null=True)

    class Meta:
        object_class = RedisRedirect
        authorization = Authorization()
        authentication = Authentication()
        validation = URLValidation()

    def get_resource_uri(self, bundle_or_obj):
        try:
            if getattr(bundle_or_obj, 'obj'):
                return "/_api/v1/redirect/%s/%s/" % (bundle_or_obj.obj.project,
                                                     bundle_or_obj.obj.slug)
            return "/_api/v1/redirect/%s/%s/" % (bundle_or_obj.project,
                                                bundle_or_obj.slug)
        except:
            return ""

    def obj_create(self, bundle, request=None, **kwargs):
        bundle.obj = RedisRedirect(**bundle.data)
        bundle = self.full_hydrate(bundle)
        if kwargs.get('delete', None):
            bundle.obj.delete()
        if not bundle.obj.save():
            raise ImmediateHttpResponse(
                HttpConflict("Object already exists")
            )
        return bundle

    def obj_update(self, bundle, request=None, **kwargs):
        if bundle.data.get('resource_uri'):
            del bundle.data['resource_uri']
        return self.obj_create(bundle, request, delete=True, **kwargs)

    def obj_get(self, request=None, pk=None, project=None, **kwargs):
        proj = RedisRedirect(slug=pk, project=project)
        if not proj.exists():
            raise NotFound("No object matching this pk")
        return proj

    def obj_get_list(self, request=None, project=None, **kwargs):
        ret_val = []
        filter_project = request.GET.get('project', None)
        filter_slug = request.GET.get('slug', None)
        if project:
            proj_obj = RedisRedirect(project=project)
            keys = proj_obj.all_slugs()
            for key in keys:
                if not filter_slug or filter_slug in key:
                    if not filter_project or filter_project in project:
                        obj = RedisRedirect(slug=key, project=project)
                        ret_val.append(obj)
        else:
            #Return all things for all projects
            indexes = r.keys("hydra:v1:projects:*:slugs")
            for index in indexes:
                index_project = index.split(":")[3]
                proj_obj = RedisRedirect(project=index_project)
                keys = proj_obj.all_slugs()
                for key in keys:
                    if not filter_slug or filter_slug in key:
                        if not filter_project or filter_project in index_project:
                            obj = RedisRedirect(slug=key, project=index_project)
                            ret_val.append(obj)
        ret_val.sort(key=lambda x: x.slug)
        return ret_val


    def obj_delete(self, request=None, **kwargs):
        obj = RedisRedirect(slug=kwargs['pk'], project=kwargs['project'])
        obj.delete()

    def obj_delete_list(self, request=None, **kwargs):
        for name in RedisRedirect.all_slugs():
            obj = RedisRedirect(name)
            obj.delete()

    def override_urls(self):
        list_url = r"^(?P<resource_name>%s)/(?P<project>[^/]+)/$"
        detail_url = r"^(?P<resource_name>%s)/(?P<project>[^/]+)/(?P<pk>.+)/$"
        return [
            url(r"^(?P<resource_name>%s)/schema/$" % self._meta.resource_name,
                self.wrap_view('get_schema'),
                name="api_get_schema"),
            url(detail_url % self._meta.resource_name,
                self.wrap_view('dispatch_detail'),
                name="api_dispatch_detail"),
            url(list_url % self._meta.resource_name,
                self.wrap_view('dispatch_list'),
                name="api_dispatch_list"),
        ]
