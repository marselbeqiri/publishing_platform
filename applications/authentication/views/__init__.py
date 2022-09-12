from applications.authentication.views.jwt_auth import (
    custom_token_obtain_pair_view,
    custom_token_refresh_view,
)
from applications.authentication.views.user_authentication import user_view, change_password_view, interests_view

__all__ = [
    "custom_token_obtain_pair_view",
    "custom_token_refresh_view",
    "user_view",
    "change_password_view",
    "interests_view"
]
