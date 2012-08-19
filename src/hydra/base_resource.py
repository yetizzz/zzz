class BaseResource(Resource):
    """
    **UNUSED**

    A base resource for all Redis-based Tastypie APIs.

    It expects you to be using the Redis Model interface, which mostly just
    boils down to save, delete, and exists.
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
                return "/_api/v1/%s/%s/" % (resource,
                                            getattr(bundle_or_obj.obj,
                                                    slug_field))
            return "/_api/v1/%s/%s/" % (resource,
                                        getattr(bundle_or_obj,
                                                slug_field))
        except:
            return ""
