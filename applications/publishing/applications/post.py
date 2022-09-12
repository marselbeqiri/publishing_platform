from django.db import models

from applications.publishing.applications.base_application import EventsApplication
from applications.publishing.domainmodels.post import PostAggregate
from applications.publishing.models.post import Post, EventPost


class PostApplication(EventsApplication):
    aggregate_class = PostAggregate
    aggregate_store_model = Post
    event_store_model = EventPost
    event_types: models.Choices = EventPost.event_type_choices
    aggregate_status_choices: models.Choices = aggregate_store_model.post_choices
