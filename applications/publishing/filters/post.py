from django_filters import rest_framework as filters

from applications.common.filters import DateFromToRangeFilter
from applications.publishing.applications import Registry

PostApplication = Registry.PostApplication


class PostFilter(filters.FilterSet):
    title = filters.CharFilter(lookup_expr="icontains")
    content = filters.CharFilter(lookup_expr="icontains")
    status = filters.NumberFilter()
    user = filters.NumberFilter()
    date = DateFromToRangeFilter(field_name='created_at')

    class Meta:
        model = PostApplication.aggregate_store_model
        fields = '__all__'
