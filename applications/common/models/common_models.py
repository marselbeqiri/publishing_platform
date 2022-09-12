from django.db import models


class Track(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Archive(models.Model):
    deleted = models.BooleanField(default=False)

    class Meta:
        abstract = True

    def delete(self, using=None, keep_parents=False):
        return self.soft_delete()

    def soft_delete(self):
        self.deleted = True
        self.save()

    def restore(self):
        self.deleted = False
        self.save()
