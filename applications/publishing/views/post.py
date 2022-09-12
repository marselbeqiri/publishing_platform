from dataclasses import asdict

from drf_yasg.utils import swagger_auto_schema
from rest_framework import serializers, exceptions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from applications.common.serializers import LabelChoiceField
from applications.publishing.applications import Registry
from applications.publishing.filters import PostFilter
from applications.publishing.typing import DataclassProtocol

__all__ = [
    "PostViewSet",
]

PostApplication = Registry.PostApplication


class PostReadSerializer(serializers.Serializer):
    id = serializers.CharField()
    title = serializers.CharField()
    content = serializers.CharField()
    slug = serializers.CharField()
    created_at = serializers.DateTimeField()
    status = serializers.ChoiceField(choices=PostApplication.aggregate_status_choices)
    status_label = LabelChoiceField(choices=PostApplication.aggregate_status_choices.choices, source="status")
    author = serializers.StringRelatedField(source="user")


class PostWriteSerializer(serializers.Serializer):
    title = serializers.CharField()
    content = serializers.CharField()
    slug = serializers.CharField()
    status = serializers.ChoiceField(choices=PostApplication.aggregate_status_choices)


class ListResponse(serializers.ListSerializer):
    child = serializers.DictField()


class PostViewSet(ModelViewSet):
    application = PostApplication
    queryset = application.list()
    post_status_choices = PostApplication.aggregate_status_choices
    filterset_class = PostFilter
    ordering_fields = [
        'created_at',
        'title',
        'content',
        'status',
        'user',
        'user__first_name',
    ]

    def get_serializer_class(self):
        serializers_ = {
            'list': PostReadSerializer,
            'retrieve': PostReadSerializer,
            'create': PostWriteSerializer,
            'update': PostWriteSerializer,
        }
        return serializers_.get(self.action, PostWriteSerializer)

    def perform_create(self, serializer):
        raw_data = {
            "data": dict(serializer.data) | {"user_id": self.request.user.id},
            "event_type": self.application.event_types.CREATED,
        }
        instance = self.application.create(raw_data)
        serializer.instance = instance

    def perform_update(self, serializer):
        data = serializer.validated_data
        if data['status'] == self.post_status_choices.DELETED:
            err_detail = {'status': ["Do not apply delete on update."]}
            raise exceptions.ValidationError(err_detail)
        post_mapping_choices = {
            self.post_status_choices.PUBLISHED: self.application.event_types.PUBLISH,
            self.post_status_choices.DRAFT: self.application.event_types.DRAFT,
            self.post_status_choices.ARCHIVED: self.application.event_types.ARCHIVED,
        }
        raw_data = {
            "data": dict(data) | {"user_id": self.request.user.id},
            "event_type": post_mapping_choices[data['status']],
            "aggregate_id": serializer.instance.id
        }
        self.application.edit(raw_data)
        serializer.instance.refresh_from_db()

    def perform_destroy(self, instance):
        raw_data = {
            "data": {"user_id": self.request.user.id},
            "event_type": self.application.event_types.DELETED,
            "aggregate_id": instance.id
        }
        self.application.edit(raw_data)

    @swagger_auto_schema(
        method='get',
    )
    @action(detail=True, methods=['get'], name='Get post change logs')
    def logs(self, _, pk: str):
        response: list[DataclassProtocol] = self.application.retrieve_aggregate_events(pk)

        json_response = [
            {**asdict(item), "event_type": str(item)}
            for item in response
        ]

        return Response(json_response)
