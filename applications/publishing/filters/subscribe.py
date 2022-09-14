from django_filters import rest_framework as filters
from drf_yasg import openapi

from applications.common.filters import DateFromToRangeFilter
from applications.publishing.models import Subscribe


class SubscribeFilter(filters.FilterSet):
    usernames = filters.BaseCSVFilter(label="usernames", method="filter_by_usernames")
    username = filters.CharFilter(label="username", field_name="subscribe_to__username")
    post_title = filters.CharFilter(label="post_title", method='filter_by_post_title')
    post_content = filters.CharFilter(label="post_content", method='filter_by_post_content')
    date = DateFromToRangeFilter(label="date", field_name='subscribe_to__posts__created_at')

    class Meta:
        model = Subscribe
        fields = [
            "usernames",
            "username",
            "post_title",
            "post_content",
            "date",
        ]

    def filter_by_post_title(self, queryset, name, value):
        return queryset.filter(subscribe_to__posts__title__icontains=value).distinct()

    def filter_by_post_content(self, queryset, name, value):
        return queryset.filter(subscribe_to__posts__content__icontains=value).distinct()

    def filter_by_usernames(self, queryset, name, value):
        return queryset.filter(subscribe_to__username__in=value).distinct()

    @classmethod
    def docs(cls):
        return [
            openapi.Parameter(
                name="usernames",
                in_=openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                description="String csv query param, which is used to have multiple search"
            ),
            openapi.Parameter(
                name="username",
                in_=openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                description="Search by specified username"
            ),
            openapi.Parameter(
                name="post_title",
                in_=openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                description="Search by subscriber post title contains"
            ),
            openapi.Parameter(
                name="post_content",
                in_=openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                description="Search by subscriber post content contains"
            ),
            openapi.Parameter(
                name="start_date",
                in_=openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                description="Filter by subscriber post after given created date"
            ),
            openapi.Parameter(
                name="end_date",
                in_=openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                description="Filter by subscriber post before given data"
            ),
        ]
