from .models import Visit


class VisitMiddleware(object):
    """Log what keys are requested when."""

    def process_view(self, request, view_func, view_args, view_kwargs):
        resource = view_kwargs.get('resource_name', '')
        if resource == 'hydra':
            if 'pk' in view_kwargs:
                Visit.objects.create(key=view_kwargs['pk'])
