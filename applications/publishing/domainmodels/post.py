import dataclasses

from rest_framework import serializers

from applications.common.event_source.domainmodel import EventSerializer, AggregateBase
from applications.common.utils import method_dispatch


# Events

# CreatePost
@dataclasses.dataclass(frozen=True)
class CreatePost:
    user_id: int
    title: str
    content: str
    slug: str
    status: int = None

    def __str__(self) -> str:
        return "CREATED"


class CreatePostSerializer(EventSerializer):
    event_class = CreatePost
    user_id = serializers.IntegerField()
    title = serializers.CharField()
    content = serializers.CharField()
    slug = serializers.CharField()


# PublishPost
@dataclasses.dataclass(frozen=True)
class PublishPost:
    user_id: int
    title: str
    content: str
    slug: str
    status: int = 0

    def __str__(self) -> str:
        return "PUBLISH"


class PublishPostSerializer(EventSerializer):
    event_class = PublishPost
    user_id = serializers.IntegerField()
    title = serializers.CharField()
    content = serializers.CharField()
    slug = serializers.CharField()
    status = serializers.IntegerField(default=0)


# DraftPost
@dataclasses.dataclass(frozen=True)
class DraftPost:
    user_id: int
    title: str
    content: str
    slug: str
    status: int = 1

    def __str__(self) -> str:
        return "DRAFT"


class DraftPostSerializer(EventSerializer):
    event_class = DraftPost
    user_id = serializers.IntegerField()
    title = serializers.CharField()
    content = serializers.CharField()
    slug = serializers.CharField()
    status = serializers.IntegerField(default=1)


# ArchivePost
@dataclasses.dataclass(frozen=True)
class ArchivePost:
    user_id: int
    status: int = 2

    def __str__(self) -> str:
        return "ARCHIVED"


class ArchivePostSerializer(EventSerializer):
    event_class = ArchivePost
    user_id = serializers.IntegerField()
    status = serializers.IntegerField(default=2)


# DeletePost
@dataclasses.dataclass(frozen=True)
class DeletePost:
    user_id: int

    def __str__(self) -> str:
        return "DELETED"


class DeletePostSerializer(EventSerializer):
    event_class = DeletePost
    user_id = serializers.IntegerField()


class PostAggregate(AggregateBase):
    _EVENT_MAP = {
        'CREATED': CreatePostSerializer,
        'PUBLISH': PublishPostSerializer,
        'DRAFT': DraftPostSerializer,
        'ARCHIVED': ArchivePostSerializer,
        'DELETED': DeletePostSerializer,
    }
    title: str
    content: str
    slug: str
    status: int
    creator_id: int
    action_by: int
    version: int

    def as_dict(self):
        return dict(
            title=self.title,
            content=self.content,
            slug=self.slug,
            status=getattr(self, 'status', None),
            user_id=self.creator_id,
            action_by=self.action_by,
            deleted=getattr(self, 'deleted', False)
        )

    def apply(self, event):
        self._apply(event)
        self._events.append(event)

    @method_dispatch
    def _apply(self, event):
        raise ValueError('Unknown event!')

    @_apply.register(CreatePost)
    def _(self, event: CreatePost):
        self.creator_id = event.user_id
        self.action_by = event.user_id
        self.title = event.title
        self.slug = event.slug
        self.content = event.content

    @_apply.register(PublishPost)
    def _(self, event: PublishPost):
        self.status = event.status
        self.action_by = event.user_id
        self.title = event.title
        self.slug = event.slug
        self.content = event.content

    @_apply.register(DraftPost)
    def _(self, event: DraftPost):
        self.status = event.status
        self.action_by = event.user_id
        self.title = event.title
        self.slug = event.slug
        self.content = event.content

    @_apply.register(ArchivePost)
    def _(self, event: ArchivePost):
        self.status = event.status
        self.action_by = event.user_id

    @_apply.register(DeletePost)
    def _(self, event: DeletePost):
        self.deleted = True
        self.status = 3
        self.action_by = event.user_id
