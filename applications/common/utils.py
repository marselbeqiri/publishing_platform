import dataclasses
import functools

from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404 as _get_object_or_404


def get_object_or_none(queryset, *filter_args, **filter_kwargs):
    """
    Same as Django's standard shortcut, but make sure to also raise 404
    if the filter_kwargs don't match the required types.
    """
    try:
        return _get_object_or_404(queryset, *filter_args, **filter_kwargs)
    except (TypeError, ValueError, ValidationError):
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
