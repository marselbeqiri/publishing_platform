from django.contrib.auth import get_user_model
from django.db.models import Count
from drf_yasg.utils import swagger_auto_schema
from rest_framework import serializers, status, mixins, exceptions
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from applications.common.utils import get_object_or_none
from applications.publishing.filters.subscribe import SubscribeFilter
from applications.publishing.models import Subscribe
from applications.publishing.serializers.member import MembersListSerializer, MembersDetailSerializer

User = get_user_model()


class SubscribersSerializer(serializers.Serializer):
    subscribed_at = serializers.DateTimeField(source="created_at", read_only=True)
    subscriber_username = serializers.CharField(source="subscriber.username", read_only=True)


class SubscribtionsSerializer(serializers.Serializer):
    subscribed_at = serializers.DateTimeField(source="created_at", read_only=True)
    subscription_username = serializers.CharField(source="subscribe_to.username", read_only=True)


class SubscribeSerializer(serializers.Serializer):
    username = serializers.CharField(write_only=True)


class MemberViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, GenericViewSet):
    queryset = User.objects.prefetch_related("interests", "subscribers", "subscriptions", "posts")
    filterset_class = None

    def get_serializer_class(self):
        serializer_map = {
            "subscribers": SubscribersSerializer,
            "subscriptions": SubscribtionsSerializer,
            "subscribe": SubscribeSerializer,
            "unsubscribe": SubscribeSerializer,
            "list": MembersListSerializer,
            "top": MembersListSerializer,
            "retrieve": MembersDetailSerializer,
        }
        return serializer_map[self.action]

    @swagger_auto_schema(
        method='get',
        responses={200: SubscribersSerializer(many=True)}
    )
    @action(detail=False, methods=['get'], name='Get Subscribers', filter_backends=[])
    def subscribers(self, request):
        queryset = request.user.subscribers.all()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        method='get',
        responses={200: SubscribtionsSerializer(many=True)},
        manual_parameters=SubscribeFilter.docs()
    )
    @action(detail=False, methods=['get'], name='Get subscriptions')
    def subscriptions(self, request):
        self.filterset_class = SubscribeFilter
        queryset = self.filter_queryset(request.user.subscriptions.all()).distinct()
        serializer = self.get_serializer(queryset, many=True)
        self.filterset_class = None
        return Response(serializer.data)

    @swagger_auto_schema(
        method='post',
    )
    @action(detail=False, methods=['post'], name='Subscribe')
    def subscribe(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        subscribe_to = get_object_or_404(User, username=serializer.validated_data['username'])
        Subscribe.objects.create(
            subscriber=request.user,
            subscribe_to=subscribe_to,
        )

        return Response(serializer.data)

    @swagger_auto_schema(
        method='post',
    )
    @action(detail=False, methods=['post'], name='Un-Subscribe')
    def unsubscribe(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        subscribe_to = get_object_or_404(User, username=serializer.validated_data['username'])

        if subscribe_to.id == request.user.id:
            err_detail = {'username': ["You can't un-subscribe yourself."]}
            raise exceptions.ValidationError(err_detail)
        if subscribe_instance := get_object_or_none(Subscribe, subscribe_to=subscribe_to, subscriber=request.user):
            subscribe_instance.delete()
        if not subscribe_instance:
            err_detail = {'username': ["You aren't subscribed to this user."]}
            raise exceptions.ValidationError(err_detail)

        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['get'], name='Top Users', )
    def top(self, _):
        queryset = self.get_queryset().annotate(
            user_total_posts=Count("posts"),
            user_total_subscriptions=Count("subscriptions")
        ).order_by("user_total_posts", "user_total_subscriptions")[:20]
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
