from datetime import datetime, timedelta

from faker import Faker
from model_bakery import baker
from rest_framework import status
from rest_framework.reverse import reverse

from applications.authentication.models import User
from applications.common.tests import BaseAPITestCase
from applications.publishing.models import Subscribe


class TestMemberViewSets(BaseAPITestCase):
    user: User

    @classmethod
    def setUpTestData(cls):
        cls.faker = Faker()
        cls.members = [
            baker.make(
                "authentication.User",
                _fill_optional=True,
                username=cls.faker.user_name() + str(index)
            )
            for index in range(100)
        ]

    def setUp(self):
        self.user = baker.make(
            "authentication.User",
            _fill_optional=True,
            username=self.faker.user_name()
        )
        self.user_subscriptions = 0
        self.user_subscribers = 0
        for member in [*self.members, self.user]:
            baker.make("publishing.Post",
                       version=1,
                       title=self.faker.catch_phrase(),
                       content=self.faker.text(),
                       user=member,
                       _fill_optional=True,
                       _quantity=10)
            if member == self.user:
                continue
            Subscribe(subscriber=self.user, subscribe_to=member).save()
            self.user_subscriptions += 1
            if member.id > 35:
                Subscribe(subscriber=member, subscribe_to=self.user).save()
                self.user_subscribers += 1

        self.login_user(self.user)

    def login_user(self, user):
        token_pair = self.get_token(user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token_pair.access_token}')

    def test__list_subscribers_200(self):
        url = reverse('member-subscribers')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), self.user_subscribers)

    def test__list_subscriptions_200(self):
        url = reverse('member-subscriptions')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), self.user_subscriptions)

    def test__filter_subscriptions_by_username(self):
        url = reverse('member-subscriptions')
        response = self.client.get(url, {'username': self.members[5].username})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test__filter_subscriptions_by_usernames(self):
        url = reverse('member-subscriptions')
        member_usernames = [member.username for member in self.members[5:10]]
        response = self.client.get(url, {'usernames': ",".join(member_usernames)})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 5)

    def test__filter_subscriptions_by_post_title(self):
        url = reverse('member-subscriptions')
        post_title = self.members[15].posts.first().title
        response = self.client.get(url, {'post_title': post_title})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test__filter_subscriptions_by_date_range(self):
        url = reverse('member-subscriptions')
        start_date = str(datetime.now().date() + timedelta(days=1))
        end_date = str(datetime.now().date() + timedelta(days=2))
        response = self.client.get(url, {'start_date': start_date, 'end_date': end_date})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

    def test__list_members_200(self):
        url = reverse('member-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 101)


class TestSubscribeFeatures(BaseAPITestCase):
    user: User

    @classmethod
    def setUpTestData(cls):
        cls.subscribe_url = reverse('member-subscribe')
        cls.unsubscribe_url = reverse('member-unsubscribe')
        cls.faker = Faker()

    def setUp(self):
        self.authorize_client()

    def test__cant_subscribe_yourself(self):
        response = self.client.post(self.subscribe_url, {'username': self.user.username})
        data = response.json()
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(data['username'], ["You can't subscribe to yourself."])

    def test__cant_subscribe_no_user(self):
        response = self.client.post(self.subscribe_url, {'username': self.faker.user_name()})
        data = response.json()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(data, {'detail': 'Not found.'})

    def test__subscribe_user(self):
        new_user = baker.make("authentication.User", _fill_optional=True, username=self.faker.user_name())
        response = self.client.post(self.subscribe_url, {'username': new_user.username})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        logged_user_subscriptions = self.user.total_subscriptions()
        self.assertEqual(logged_user_subscriptions, 1)

    def test__cant_subscribe_same_user(self):
        new_user = baker.make("authentication.User", _fill_optional=True, username=self.faker.user_name())
        response = self.client.post(self.subscribe_url, {'username': new_user.username})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        error_response = self.client.post(self.subscribe_url, {'username': new_user.username})
        self.assertEqual(error_response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(error_response.data['username'][0], 'You are subscribed to this user')

    def test__cant_unsubscribe_no_user(self):
        response = self.client.post(self.unsubscribe_url, {'username': self.faker.user_name()})
        data = response.json()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(data, {'detail': 'Not found.'})

    def test__cant_unsubscribe_yourself(self):
        response = self.client.post(self.unsubscribe_url, {'username': self.user.username})
        data = response.json()
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(data, {'username': ["You can't un-subscribe yourself."]})

    def test__unsubscribe(self):
        users = baker.make("authentication.User", _fill_optional=True, _quantity=50)
        for user in users:
            response = self.client.post(self.subscribe_url, {'username': user.username})
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            del response

        logged_user_subscriptions = self.user.total_subscriptions()
        self.assertEqual(logged_user_subscriptions, 50)

        for _user in users[:10]:
            response = self.client.post(self.unsubscribe_url, {'username': _user.username})
            self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        self.user.refresh_from_db()
        self.assertEqual(self.user.total_subscriptions(), 40)

    def test__cant_unsubscribe_not_subscribed_user(self):
        new_user = baker.make("authentication.User", _fill_optional=True, username=self.faker.user_name())
        response = self.client.post(self.unsubscribe_url, {'username': new_user.username})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json(), {'username': ["You aren't subscribed to this user."]})
