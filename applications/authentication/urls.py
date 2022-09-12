from django.urls import path

from applications.authentication.views import (
    custom_token_obtain_pair_view,
    custom_token_refresh_view,
    user_view,
    change_password_view,
    interests_view
)

urlpatterns = [
    path("token/", custom_token_obtain_pair_view, name="token_obtain_pair"),
    path("token/refresh/", custom_token_refresh_view, name="token_refresh"),
    path("user/", user_view, name="user_view"),
    path("user/interests/", interests_view, name="interests_view"),
    path("user/change-password/", change_password_view, name="change_password"),
]
