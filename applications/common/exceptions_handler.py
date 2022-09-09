from rest_framework.exceptions import ValidationError
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status


def records_to_list(records):
    return [str(record) for record in records]


def custom_exception_handler(exc, context):
    """
    Returns the response that should be used for any given exception.

    By default we handle the REST framework `APIException`, and also
    Django's built-in `Http404` and `PermissionDenied` exceptions.

    Any unhandled exceptions may return `None`, which will cause a 500 error
    to be raised.
    """
    if response := exception_handler(exc, context):
        return response
    if context.get('password_action'):
        return Response({'password': exc.messages}, status=status.HTTP_400_BAD_REQUEST)

    return None
