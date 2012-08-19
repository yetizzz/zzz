from django.db import models


class Visit(models.Model):
    when = models.DateTimeField(auto_now_add=True, db_index=True)
    project = models.CharField(max_length=255, db_index=True)
    slug = models.CharField(max_length=255, db_index=True)
    retval = models.TextField(null=True, blank=True)
