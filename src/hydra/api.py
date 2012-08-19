import redis

from django.conf.urls import url

from tastypie.resources import Resource
from tastypie import fields
from tastypie.authorization import Authorization
from tastypie.authentication import Authentication
from tastypie.exceptions import NotFound

from hydra.utils import (r, make_slug, remove_slug, save,
                         get_range, get_keys, delete, get_urls)


"""
"hydra:v1:projects" = Set of projects
"hydra:v1:projects:<project>" = Metadata
GET /api/v1/projects/
    List of Projects
GET /api/v1/projects/<project>/
    Metadata on Project
    resource_uri -> /slugs/

"hydra:v1:projects:<project>:slugs" = Set of slugs
GET /api/v1/projects/<project>/slugs/
    Slugs for a project
"hydra:v1:projects:<project>:slugs:<slug>" = Actual Data
GET /api/v1/projects/<project>/slugs/<slug>/
    Detail view for slug
"""

class RedisProject(object):
    index_slug = "hydra:v1:projects"

    def __init__(self, name=None, whitelist=None, *args, **kwargs):
        super(RedisProject, self).__init__(*args, **kwargs)
        self.name = name
        if whitelist:
            self.whitelist = whitelist
        else:
            self.whitelist = self.get_whitelist()

    @classmethod
    def all_projects(cls):
        return r.smembers(cls.index_slug)

    @classmethod
    def make_key(cls, key):
        return "hydra:v1:projects:%s" % (key)

    @property
    def slug(self):
        return "hydra:v1:projects:%s" % (self.name)

    def save_whitelist(self):
        for url in self.whitelist:
            r.sadd("%s:whitelist" % self.slug, url)

    def save_project(self):
        r.hset(self.slug, "exists", "true")
        r.sadd(self.index_slug, self.name)

    def save(self):
        self.save_whitelist()
        self.save_project()

    def exists(self):
        return r.hget(self.slug, "exists") == "true"

    def get_whitelist(self):
        return r.smembers("%s:whitelist" % self.slug)

class ProjectResource(Resource):
    name = fields.CharField(attribute='name')
    whitelist = fields.ListField(attribute="whitelist")

    class Meta:
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
        bundle.obj = RedisProject(bundle.data)
        bundle = self.full_hydrate(bundle)
        bundle.obj.save()
        return bundle

    def obj_get(self, request=None, pk=None, **kwargs):
        proj = RedisProject(pk)
        if not proj.exists():
            raise NotFound("No object matching this pk")
        return proj

    def obj_get_list(self, request=None, **kwargs):
        ret_val = []
        keys = RedisProject.all_projects()
        for key in keys:
            obj = RedisProject(key)
            ret_val.append(obj)
        return ret_val

    def obj_update(self, bundle, request=None, **kwargs):
        return self.obj_create(bundle, request, **kwargs)

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
            self.get_urls()

    @property
    def index_slug(self):
        return "hydra:v1:projects:%s:slugs" % (self.project)

    @property
    def redis_slug(self):
        return "%s:%s" % (self.index_slug, self.slug)

    def all_slugs(self):
        return r.smembers(self.index_slug)

    def make_key(cls, key):
        return "%s:%s" % (self.index_slug, key)

    def save_redirect(self):
        r.zincrby(self.redis_slug, self.urls[0], 1)
        r.sadd(self.index_slug, self.slug)

    def save(self):
        if not self.exists():
            self.save_redirect()

    def exists(self):
        return r.zcard(self.redis_slug)

    def get_urls(self):
        self._urls = r.zrevrange(self.redis_slug, 0, -1, withscores=True)
        self.urls = []
        for obj in self._urls:
            redirect_url, score = obj
            self.urls.append({
                'score': score,
                'url': redirect_url
            })


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
                return "/_api/v1/redirect/%s/%s" % (bundle_or_obj.obj.project,
                                                    bundle_or_obj.obj.slug)
            return "/_api/v1/redirect/%s/%s" % (bundle_or_obj.project,
                                                bundle_or_obj.slug)
        except:
            return ""

    def obj_create(self, bundle, request=None, **kwargs):
        bundle.obj = RedisRedirect(**bundle.data)
        bundle = self.full_hydrate(bundle)
        bundle.obj.save()
        return bundle

    def obj_get(self, request=None, pk=None, project=None, **kwargs):
        proj = RedisRedirect(slug=pk, project=project)
        if not proj.exists():
            raise NotFound("No object matching this pk")
        return proj

    def obj_get_list(self, request=None, project=None, **kwargs):
        ret_val = []
        proj_obj = RedisRedirect(project=project)
        keys = proj_obj.all_slugs()
        for key in keys:
            obj = RedisRedirect(slug=key, project=project)
            ret_val.append(obj)
        return ret_val

    def obj_update(self, bundle, request=None, **kwargs):
        return self.obj_create(bundle, request, **kwargs)

    def obj_delete(self, request=None, **kwargs):
        obj = RedisRedirect(kwargs['pk'])
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
