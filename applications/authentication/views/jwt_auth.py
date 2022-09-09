from rest_framework_simplejwt.views import TokenViewBase

from applications.authentication import serializers


class TokenObtainPairView(TokenViewBase):
    """
    Takes a set of user credentials and returns an access and refresh JSON web
    token pair to prove the authentication of those credentials.
    """

    serializer_class = serializers.TokenObtainPairSerializer


custom_token_obtain_pair_view = TokenObtainPairView.as_view()


class TokenRefreshView(TokenViewBase):
    """
    Takes a refresh type JSON web token and returns an access type JSON web
    token if the refresh token is valid.
    """

    serializer_class = serializers.TokenRefreshSerializer


custom_token_refresh_view = TokenRefreshView.as_view()
