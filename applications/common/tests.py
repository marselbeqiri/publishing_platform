from django.contrib.auth import get_user_model
from faker import Faker
from model_bakery import baker
from rest_framework.reverse import reverse
from rest_framework.test import APIClient, APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()


class BaseAPITestCase(APITestCase):
    faker: Faker
    client: APIClient
    user: User

    @staticmethod
    def get_url_with_pk(viewname: str, pk: int | str) -> str:
        return reverse(viewname, kwargs={'pk': pk})

    def authorize_client(self):
        self.user = baker.make("authentication.User", _fill_optional=True)
        token_pair = self.get_token(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token_pair.access_token}')

    @classmethod
    def get_token(cls, user):
        return RefreshToken.for_user(user)
