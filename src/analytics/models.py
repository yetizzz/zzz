from django.db import models


class Visit(models.Model):
    when = models.DateTimeField(auto_now_add=True, db_index=True)
    key = models.CharField(max_length=255, db_index=True)
