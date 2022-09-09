from faker import Faker
from model_bakery import baker
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient, APITestCase

from applications.authentication.models import User


class TestUserRegister(APITestCase):
    faker: Faker
    user_payload: dict

    @classmethod
    def setUpTestData(cls):
        cls.faker = Faker()
        cls.user_payload = {
            "username": cls.faker.user_name(),
            "email": cls.faker.email(),
            "first_name": cls.faker.first_name(),
            "last_name": cls.faker.last_name(),
            "password": cls.faker.password()
        }

    def test__user_creation(self):
        response = self.client.post(
            path=reverse("user_view"),
            data=self.user_payload,
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['username'], self.user_payload['username'])
        self.assertEqual(response.data['email'], self.user_payload['email'])
        self.assertTrue(response.data['refresh'])
        self.assertTrue(response.data['access'])


class TestUserGetRetrieveUpdate(APITestCase):
    faker: Faker
    apiclient: APIClient
    user: User
    default_password = 'password'

    @classmethod
    def setUpTestData(cls):
        cls.faker = Faker()
        cls.user = baker.make("authentication.User", _fill_optional=True)
        cls.user.set_password(cls.default_password)

    def setUp(self) -> None:
        self.client.force_authenticate(user=self.user)

    def test__user__data_put(self):
        old_first_name = self.user.first_name
        old_last_name = self.user.last_name
        put_payload = {
            "first_name": self.faker.first_name(),
            "last_name": self.faker.last_name(),
            "email": self.faker.email(),
        }
        response = self.client.put(
            path=reverse("user_view"),
            data=put_payload,
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertNotEqual(self.user.first_name, old_first_name)
        self.assertNotEqual(self.user.last_name, old_last_name)
        self.assertEqual(self.user.first_name, put_payload['first_name'])
        self.assertEqual(self.user.last_name, put_payload['last_name'])
        self.assertEqual(self.user.email, put_payload['email'])

    def test__user__data_patch(self):
        old_email = self.user.email
        patch_payload = {
            "email": self.faker.email(),
        }
        response = self.client.patch(
            path=reverse("user_view"),
            data=patch_payload,
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertNotEqual(self.user.email, old_email)
        self.assertEqual(self.user.email, patch_payload['email'])

    def test__change_password(self):
        payload = {
            "old_password": self.default_password,
            "new_password": self.faker.password()
        }
        response = self.client.put(
            path=reverse("change_password"),
            data=payload,
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password(payload['new_password']))
