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
        r.srem(self.index_slug, self.name)

    def exists(self):
        return r.hget(self.redis_slug, "exists") == "true"

    def get_whitelist(self):
        return r.smembers("%s:whitelist" % self.redis_slug)

class BaseResource(object):
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
        r.sadd(self.index_slug, self.slug)

    def save_urls(self):
        for obj in self.urls:
            if hasattr(obj, 'get'):
                if obj.get('score', None):
                    r.zadd(self.redis_slug, int(obj['score']), obj['url'])
            else:
                print "WTF?!"
                r.zincrby(self.redis_slug, self.urls[0], 1)

    def save(self):
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
        self._urls = r.zrevrange(self.redis_slug, 0, -1, withscores=True)
        self.urls = []
        for obj in self._urls:
            redirect_url, score = obj
            self.urls.append({
                'score': score,
                'url': redirect_url
            })
        return self.urls


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
