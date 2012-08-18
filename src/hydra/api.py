from tastypie.resources import Resource
from tastypie import fields
from tastypie.authorization import Authorization
from tastypie.authentication import Authentication
from tastypie.exceptions import ImmediateHttpResponse
from tastypie.http import HttpConflict
import redis

from collections import defaultdict

r = redis.Redis()

def make_key(val):
    return "hydra:v1:redirect:%s" % val

def remove_key(val):
    return val.replace("hydra:v1:redirect:", "")

def is_valid_key(key):
    redis_key = make_key(key)
    keys = r.keys(redis_key)
    if keys:
        return False
    return True


def save(key, url):
    redis_key = make_key(key)
    r.set(redis_key, url)

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
        print "Redis: %s -> %s" % (self.key, self.url)


class HydraResource(Resource):
    key = fields.CharField(attribute='key')
    url = fields.CharField(attribute='url')

    class Meta:
        object_class = RedisObject
        authorization=Authorization()
        authentication=Authentication()

    def get_resource_uri(self, bundle_or_obj):
        try:
            if getattr(bundle_or_obj, 'obj'):
                return "/api/v1/hydra/%s" % remove_key(bundle_or_obj.obj.key)
            return "/api/v1/hydra/%s" % remove_key(bundle_or_obj.key)
        except:
            return ""

    def obj_create(self, bundle, request=None, **kwargs):
        bundle.obj  = RedisObject(bundle.data)
        bundle = self.full_hydrate(bundle)
        if not is_valid_key(bundle.obj.key):
            raise ImmediateHttpResponse(
                HttpConflict("Already exists")
                )
        save(bundle.obj.key, bundle.obj.url)
        return bundle.obj

    def obj_get(self, request=None, pk=None, **kwargs):
        value = r.get(make_key(pk))
        ret_obj = RedisObject()
        ret_obj.key = pk
        ret_obj.url = value
        return ret_obj

    def obj_get_list(self, request=None, **kwargs):
        ret_val = []
        keys = r.keys(make_key('*'))
        if keys:
            values = r.mget(keys)
        else:
            values = []
        for index, key in enumerate(keys):
            ret_obj = RedisObject()
            value = values[index]
            ret_obj.key = key
            ret_obj.url = values[index]
            ret_val.append(ret_obj)
        return ret_val

    def rollback(self, bundles):
        pass
