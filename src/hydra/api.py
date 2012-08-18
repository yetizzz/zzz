from tastypie.resources import Resource
from tastypie import fields
from tastypie.authorization import Authorization
from tastypie.authentication import Authentication
from tastypie.exceptions import ImmediateHttpResponse
from tastypie.http import HttpConflict
import redis


r = redis.StrictRedis()

def make_slug(val):
    return "hydra:v1:redirects:%s" % val

def remove_slug(val):
    return val.replace("hydra:v1:redirects:", "")

def save(slug, url):
    redis_slug = make_slug(slug)
    r.zincrby(redis_slug, url, 1)
    #r.set(redis_slug, urls)

def get_urls(slug):
    ret_val = []
    values = r.zrange(make_slug(slug), 0, -1, withscores=True)
    for value in values:
        url, score = value
        ret_val.append({
            'score': score,
            'url': url
        })
    return ret_val


class RedisObject(object):

    def __init__(self, initial=None):
        self.__dict__['_data'] = {}

        if hasattr(initial, 'items'):
            self.__dict__['_data'] = initial

    def __getattr__(self, name):
        return self._data.get(name, None)

    def __setattr__(self, name, value):
        self.__dict__['_data'][name] = value

    def to_dict(self):
        return self._data

    def __unicode__(self):
        print "Redis: %s -> %s" % (self.slug, self.urls)

    def save(self):
        pass

    def inc(self):
        pass

    def delete(self):
        pass


class HydraResource(Resource):
    slug = fields.CharField(attribute='slug')
    urls = fields.ListField(attribute='urls', null=True)

    class Meta:
        object_class = RedisObject
        authorization = Authorization()
        authentication = Authentication()

    def detail_uri_kwargs(self, bundle_or_obj):
        kwargs = {}

        if isinstance(bundle_or_obj, Bundle):
            kwargs['pk'] = bundle_or_obj.obj.slug
        else:
            kwargs['pk'] = bundle_or_obj.slug

        return kwargs

    def get_resource_uri(self, bundle_or_obj):
        try:
            if getattr(bundle_or_obj, 'obj'):
                return "/api/v1/hydra/%s" % remove_slug(bundle_or_obj.obj.slug)
            return "/api/v1/hydra/%s" % remove_slug(bundle_or_obj.slug)
        except:
            return ""

    def obj_create(self, bundle, request=None, **kwargs):
        bundle.obj = RedisObject(bundle.data)
        bundle = self.full_hydrate(bundle)
        save(bundle.obj.slug, bundle.obj.urls[0])
        return bundle.obj

    def obj_get(self, request=None, pk=None, **kwargs):
        ret_val = RedisObject()
        ret_val.urls = []
        ret_val.slug = pk
        values = r.zrange(make_slug(pk), 0, -1, withscores=True)
        for value in values:
            url, score = value
            ret_val.urls.append({
                'score': score,
                'url': url
            })
        return ret_val

    def obj_get_list(self, request=None, **kwargs):
        ret_val = []
        keys = r.keys(make_slug('*'))
        for key in keys:
            ret_obj = RedisObject()
            ret_obj.urls = []
            ret_obj.slug = remove_slug(key)
            ret_obj.urls = get_urls(remove_slug(key))
            ret_val.append(ret_obj)
        return ret_val

    def obj_update(self, bundle, request=None, **kwargs):
        return self.obj_create(bundle, request, **kwargs)

    def obj_delete(self, request=None, **kwargs):
        r.delete(make_slug(kwargs['pk']))

    def obj_delete_list(self, request=None, **kwargs):
        for slug in r.keys('*'):
            r.delete(slug)

    def rollback(self, bundles):
        pass
