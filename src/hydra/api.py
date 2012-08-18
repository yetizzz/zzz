import redis

from django.conf.urls import url

from tastypie.resources import Resource
from tastypie import fields
from tastypie.authorization import Authorization
from tastypie.authentication import Authentication
from tastypie.exceptions import NotFound

from hydra.utils import (r, make_slug, remove_slug, save,
                         get_range, get_keys, delete, get_urls)

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

    def get_resource_uri(self, bundle_or_obj):
        try:
            if getattr(bundle_or_obj, 'obj'):
                return "/_api/v1/hydra/%s" % remove_slug(bundle_or_obj.obj.slug)
            return "/_api/v1/hydra/%s" % remove_slug(bundle_or_obj.slug)
        except:
            return ""

    def obj_create(self, bundle, request=None, **kwargs):
        bundle.obj = RedisObject(bundle.data)
        bundle = self.full_hydrate(bundle)
        save(bundle.obj.slug, bundle.obj.urls[0])
        return bundle.obj

    def obj_get(self, request=None, pk=None, **kwargs):
        values = get_range(pk)
        if not values:
            raise NotFound("No object matching this pk")
        ret_val = RedisObject()
        ret_val.urls = []
        ret_val.slug = pk
        for value in values:
            redirect_url, score = value
            ret_val.urls.append({
                'score': score,
                'url': redirect_url
            })
        return ret_val

    def obj_get_list(self, request=None, **kwargs):
        ret_val = []
        filter_slug = request.GET.get('slug', None)
        if not filter_slug:
            #Support ?q= format also
            filter_slug = request.GET.get('q', None)
        if filter_slug:
            keys = get_keys('%s*' % filter_slug)
        else:
            keys = get_keys("*")
        for key in keys:
            base_key = remove_slug(key)
            ret_obj = RedisObject()
            ret_obj.urls = []
            ret_obj.slug = base_key
            ret_obj.urls = get_urls(base_key)
            ret_val.append(ret_obj)
        return ret_val

    def obj_update(self, bundle, request=None, **kwargs):
        return self.obj_create(bundle, request, **kwargs)

    def obj_delete(self, request=None, **kwargs):
        delete(kwargs['pk'])

    def obj_delete_list(self, request=None, **kwargs):
        for slug in get_keys('*'):
            r.delete(slug)

    def override_urls(self):
        raw_url = r"^(?P<resource_name>%s)/(?P<pk>^(schema)[^/]+)$"
        return [
            url(r"^(?P<resource_name>%s)/schema/$" % self._meta.resource_name, self.wrap_view('get_schema'), name="api_get_schema"),
            url(raw_url % self._meta.resource_name,
                self.wrap_view('dispatch_detail'),
                name="api_dispatch_detail"),
        ]
