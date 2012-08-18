Our epic Django Dash project.


API
---

```rest
    GET /api/v1/redirect/
    [
        "slugs": {
            "queryset",
            "awesome",
            "google"
        }
    ]

    GET /api/v1/redirct/?slug=django
    [
        "slugs": {
            "django-slug-utils",
            "django-awesome",
        }
    ]

    POST /api/v1/redirect/<slug>/
        {"url": "http://django.rtfd.org/docs/queryset.html"}

    GET /api/v1/redirect/<slug>/
        [
            {
                "count": 5,
                "url": "http://django.rtfd.org/docs/queryset.html"
            },
            {
                "count": 3,
                "url": "http://django.rtfd.org/docs/bullshit.html"
            }
        ]


    DELETE /api/v1/redirect/<slug>/

    PUT /api/v1/redirect/<slug>/

```
