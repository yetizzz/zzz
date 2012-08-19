Our epic Django Dash project.


API
---

```rest
    GET /api/v1/projects/<project>/slugs/<slug>/
        Detail view for slug

    # List of projects
    GET /api/v1/projects/?format=json
    {
        "meta": {},
        "objects": [
            {
                "name": "readthedocs",
                "resource_uri": "/_api/v1/project/readthedocs/",
                "whitelist": [
                    "djangoproject.com",
                    "readthedocs.org"
                ]
            },
            {
                "name": "fabric",
                "resource_uri": "/_api/v1/project/fabric/",
                "whitelist": [
                    "djangoproject.com",
                    "fabfile.org"
                ]
            }
        ]
    }

    # Project Detail
    GET /api/v1/projects/<project>/
    {
        "name": "django",
        "resource_uri": "/_api/v1/project/django/",
        "whitelist": [
            "djangoproject.com",
            "readthedocs.org"
        ]
    }

    GET /api/v1/redirect/?format=json
    {
        "meta": {},
        "objects": [
            {
                "project": "django",
                "resource_uri": "/_api/v1/redirect/django/get_object/",
                "slug": "get_object",
                "urls": [
                    {
                        "score": 1.0,
                        "url": "http://django.readthedocs.org/en/latest/ref/class-based-views/mixins-single-object.html#django.views.generic.detail.SingleObjectMixin.get_object"
                    }
                ]
            }
        ]
    }

    GET /api/v1/redirect/django/get_object/?format=json

    {
        "project": "django",
        "resource_uri": "/_api/v1/redirect/django/get_object/",
        "slug": "get_object",
        "urls": [
            {
                "score": 1.0,
                "url": "http://django.readthedocs.org/en/latest/ref/class-based-views/mixins-single-object.html#django.views.generic.detail.SingleObjectMixin.get_object"
            }
        ]
    }

    DELETE /api/v1/redirect/django/get_object/

    PUT /api/v1/redirect/django/get_object/

```


Redis Data Model

```
    "hydra:v1:projects" = Index of projects <Set>
    "hydra:v1:projects:<project>" = Project Metadata <Hash>
    "hydra:v1:projects:<project>:slugs" = Index of slugs <Set>
    "hydra:v1:projects:<project>:slugs:<slug>" = Slug Data <SortedSet>
```


```
