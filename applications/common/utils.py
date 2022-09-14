import dataclasses
import functools
from typing import Type

from django.core.exceptions import ValidationError
from django.http import Http404
from django.shortcuts import get_object_or_404 as _get_object_or_404
from django_filters import rest_framework as filters
from drf_yasg import openapi


def get_object_or_none(queryset, *filter_args, **filter_kwargs):
    """
    Same as Django's standard shortcut, but make sure to also raise 404
    if the filter_kwargs don't match the required types.
    """
    try:
        return _get_object_or_404(queryset, *filter_args, **filter_kwargs)
    except (TypeError, ValueError, ValidationError, Http404):
        return None


def method_dispatch(func):
    dispatcher = functools.singledispatch(func)

    def wrapper(*args, **kw):
        return dispatcher.dispatch(args[1].__class__)(*args, **kw)

    wrapper.register = dispatcher.register
    functools.update_wrapper(wrapper, func)
    return wrapper


def get_dataclass_fields(dataclass: dataclasses.dataclass) -> list:
    fields: dict = dataclass.__dataclass_fields__
    return list(fields.keys())


def query_param_yasg(filter_class: Type[filters.FilterSet]):
    return [
        openapi.Parameter(
            name=name,
            in_=openapi.IN_QUERY,
            type=openapi.TYPE_STRING
        )
        for name, filter_field in filter_class.declared_filters.items()
    ]
