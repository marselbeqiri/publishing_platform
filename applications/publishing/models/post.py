import uuid

from django.db import models

from applications.common.models.event_source import EventModel, AggregateModel


class PostChoices(models.IntegerChoices):
    PUBLISHED = 0
    DRAFT = 1
    ARCHIVED = 2
    DELETED = 3


class Post(AggregateModel):
    post_choices = PostChoices
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(verbose_name="Post title", max_length=255)
    content = models.TextField(verbose_name="Post Content")
    slug = models.CharField(verbose_name="Post slug", max_length=255)
    version = models.PositiveIntegerField(verbose_name="Event Version", default=1)
    status = models.PositiveIntegerField(choices=post_choices.choices, default=post_choices.PUBLISHED)
    author = models.ForeignKey(
        verbose_name="Author",
        to="authentication.User",
        related_name="posts",
        on_delete=models.CASCADE
    )
    action_by = models.PositiveIntegerField()

    class Meta:
        verbose_name = "User Post"
        verbose_name_plural = "User Posts"
        ordering = ["created_at"]

    @property
    def user_id(self):
        return self.action_by

    @user_id.setter
    def user_id(self, user_id: id):
        self.action_by = user_id


class EventPostChoices(models.TextChoices):
    PUBLISH: str = "PUBLISH"
    DRAFT: str = "DRAFT"
    CREATED: str = "CREATED"
    ARCHIVED: str = "ARCHIVED"
    DELETED: str = "DELETED"


class EventPost(EventModel):
    event_type_choices = EventPostChoices
    event_type = models.CharField(max_length=100, choices=event_type_choices.choices)
    aggregate = models.ForeignKey(to=Post, on_delete=models.CASCADE, related_name="events")

    class Meta:
        verbose_name = "Post Event"
        verbose_name_plural = "Posts Events"
        ordering = ["created_at"]

    def to_raw_data(self) -> dict:
        return dict(
            event_type=self.event_type,
            aggregate_id=self.aggregate_id,
            data=self.data,
        )
