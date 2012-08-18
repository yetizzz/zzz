from tastypie.resources import ModelResource

from .models import Visit


class VisitResource(ModelResource):

    class Meta:
        queryset = Visit.objects.all()
        resource_name = 'visits'
        allowed_methods = ('get',)
