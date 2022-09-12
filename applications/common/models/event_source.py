import uuid

from django.db import models

from applications.common.models import Track
from applications.common.models.common_models import Archive


class EventModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    data = models.JSONField("Data", default=dict)
    event_type = models.CharField(max_length=100)

    aggregate = None  # relationship, override

    class Meta:
        abstract = True

    def delete(self, using=None, keep_parents=False):  # Deactivate Deletion
        pass

    def to_raw_data(self):
        raise NotImplementedError


class AggregateModel(Track, Archive):
    class Meta:
        abstract = True
