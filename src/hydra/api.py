"""
A redis-based Tastypie API.

It adds has "Model" type objects RedisProject and RedisRedirect. These are used for all of the data access, and for hydration at the Tatypie level.

Then we have resources that are based on these models. The ProjectResource and RedirectResource map onto the model objects listed above.

This could be a generic interface, and the code is most of the way there to making a moderately generic BaseResource for interacting with Redis Models.
"""
import redis

from django.conf.urls import url
from django.conf import settings

from tastypie.resources import Resource
from tastypie import fields
from tastypie.authorization import Authorization
from tastypie.authentication import Authentication
from tastypie.exceptions import NotFound, ImmediateHttpResponse
from tastypie.http import HttpConflict

r = redis.StrictRedis.from_url(settings.REDIS_URL)


class RedisProject(object):
    """
    A model layer repsenting a Project in Redis.

    It has an index of all existing projects, and then contains metadata about projects including their existence, and a whitelist of URLs that you can link to from them.

    Generally you create an instance by passing in a name, and a possible whitelist. If you only pass in the name, the whitelist is populated from the data store.

    The main methods you will call on an instance are save, delete, and exists. There is a classmethod called all_projects that will return all projects.

    """
    index_slug = "hydra:v1:projects"

    def __init__(self, name=None, whitelist=None, *args, **kwargs):
        super(RedisProject, self).__init__(*args, **kwargs)
        #if not name:
            #raise ValueError("Projects need a name")
        self.name = name
        if whitelist:
            self.whitelist = whitelist
        else:
            # We need to populate the whitelist here,
            # so when we return the object, it will serialize with them
            self.whitelist = self.get_whitelist()

    @classmethod
    def all_projects(cls):
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

class BaseResource(Resource):
    """
    Not used yet
    """
    def obj_update(self, bundle, request=None, **kwargs):
        if bundle.data.get('resource_uri'):
            del bundle.data['resource_uri']
        return self.obj_create(bundle, request, delete=True, **kwargs)

    def obj_create(self, bundle, request=None, **kwargs):
        bundle.obj = self._meta.object_class(**bundle.data)
        bundle = self.full_hydrate(bundle)
        if kwargs.get('delete', None):
            bundle.obj.delete()
        bundle.obj.save()
        return bundle

    def obj_get(self, request=None, **kwargs):
        proj = self._meta.object_class(**kwargs)
        if not proj.exists():
            raise NotFound("No object matching this pk")
        return proj

    def obj_delete(self, request=None, **kwargs):
        obj = self._meta.object_class(**kwargs)
        obj.delete()

    def _find_slug(self):
        if self.fields.get('slug'):
            return 'slug'
        if self.fields.get('name'):
            return 'name'

    def get_resource_uri(self, bundle_or_obj):
        resource = self._meta.resource_name
        slug_field = self._find_slug()
        try:
            if getattr(bundle_or_obj, 'obj'):
                return "/_api/v1/%s/%s/" % (resource, getattr(bundle_or_obj.obj, slug_field))
            return "/_api/v1/%s/%s/" % (resource, getattr(bundle_or_obj, slug_field))
        except:
            return ""

class ProjectResource(Resource):
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
            url(r"^(?P<resource_name>%s)/schema/$" % self._meta.resource_name, self.wrap_view('get_schema'), name="api_get_schema"),
            url(raw_url % self._meta.resource_name,
                self.wrap_view('dispatch_detail'),
                name="api_dispatch_detail"),
        ]

class RedisRedirect(object):

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


class RedirectResource(Resource):
    slug = fields.CharField(attribute='slug')
    project = fields.CharField(attribute='project')
    urls = fields.ListField(attribute='urls', null=True)

    class Meta:
        object_class = RedisRedirect
        authorization = Authorization()
        authentication = Authentication()

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
            url(r"^(?P<resource_name>%s)/schema/$" % self._meta.resource_name, self.wrap_view('get_schema'), name="api_get_schema"),
            url(detail_url % self._meta.resource_name,
                self.wrap_view('dispatch_detail'),
                name="api_dispatch_detail"),
            url(list_url % self._meta.resource_name,
                self.wrap_view('dispatch_list'),
                name="api_dispatch_list"),
        ]
