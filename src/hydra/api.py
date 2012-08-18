from tastypie.resources import Resource
from tastypie import fields
import redis

from collections import defaultdict

r = redis.Redis()

def make_key(val):
    return "hydra:v1:redirect:%s" % val


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


class HydraResource(Resource):
    key = fields.CharField(attribute='key')
    url = fields.CharField(attribute='url')

    #keys = redis.key('hydra:v1:redirect:*')

    def obj_create(self, bundle, request=None, **kwargs):
        print kwargs

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
