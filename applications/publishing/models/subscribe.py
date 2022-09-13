import uuid

from django.db import models
from rest_framework import exceptions


class SubscriberChoices(models.IntegerChoices):
    SUBSCRIBE = 0
    UNSUBSCRIBE = 1


class Subscribe(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    subscriber = models.ForeignKey(
        verbose_name="Subscribed Author",
        to="authentication.User",
        related_name="subscriptions",
        on_delete=models.CASCADE
    )
    subscribe_to = models.ForeignKey(
        verbose_name="Subscribed Author",
        to="authentication.User",
        related_name="subscribers",
        on_delete=models.CASCADE
    )

    class Meta:
        verbose_name = "Subscribe"
        verbose_name_plural = "Subscribes"
        ordering = ["created_at"]
        unique_together = ['subscriber', 'subscribe_to']

    def validate_commit(self):
        if self.subscriber.subscriptions.count() > 100:
            err_detail = {'username': ["You can't subscribe this user since you have reached 100 subscriptions."]}
            raise exceptions.ValidationError(err_detail)

        if self.subscriber.id == self.subscribe_to.id:
            err_detail = {'username': ["You can't subscribe to yourself."]}
            raise exceptions.ValidationError(err_detail)

        if self.__class__.objects.filter(subscriber=self.subscriber, subscribe_to=self.subscribe_to).exists():
            err_detail = {'username': ["You are subscribed to this user"]}
            raise exceptions.ValidationError(err_detail)

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        self.validate_commit()
        super().save(force_insert, force_update, using, update_fields)
