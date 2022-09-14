from faker import Faker
from rest_framework import status
from rest_framework.reverse import reverse

from applications.authentication.models import User
from applications.common.tests import BaseAPITestCase
from applications.publishing.models import Post, EventPost


class TestPostListCreateViewSet(BaseAPITestCase):
    user: User

    @classmethod
    def setUpTestData(cls):
        cls.list_create_post_url = reverse('post-list')
        cls.faker = Faker()
        cls.create_payload = dict(
            title=cls.faker.catch_phrase(),
            content=cls.faker.text(),
            slug=cls.faker.uri_path(),
            status=0,
        )

    @classmethod
    def _publish_payload(cls, status_=0):
        return dict(
            title=cls.faker.catch_phrase(),
            content=cls.faker.text(),
            slug=cls.faker.uri_path(),
            status=status_,
        )

    def setUp(self):
        self.authorize_client()

    def test__create_post(self):
        payload = self._publish_payload()
        response = self.client.post(self.list_create_post_url, payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.json(), payload)
        post = Post.objects.all().last()
        self.assertEqual(post.status, 0)
        total_events = EventPost.objects.filter(aggregate=post).count()
        self.assertEqual(total_events, 1)

    def test__get_post_list(self):
        payload = self._publish_payload()
        self.client.post(self.list_create_post_url, payload)
        response = self.client.get(self.list_create_post_url)
        data = response.json()
        results = data['results']
        self.assertEqual(data['count'], 1)
        self.assertEqual(results[0]['title'], payload['title'])
        self.assertEqual(results[0]['content'], payload['content'])
        self.assertEqual(results[0]['slug'], payload['slug'])
        self.assertEqual(results[0]['status'], 0)

    def _create_post(self):
        payload = self._publish_payload()
        self.client.post(self.list_create_post_url, payload)

    def _create_multiple_posts(self, quantity=10):
        for post in range(quantity):
            self._create_post()

    def test__post_list_filter_by_title(self):
        self._create_multiple_posts(50)
        response = self.client.get(self.list_create_post_url, {"title": "ct"})
        data = response.json()
        self.assertLess(data['count'], 50)

        second_response = self.client.get(self.list_create_post_url, {"title": data['results'][0]['title']})
        second_data = second_response.json()
        self.assertEqual(second_data['count'], 1)


class TestUpdateDeleteViewSet(BaseAPITestCase):
    user: User

    @classmethod
    def setUpTestData(cls):
        cls.faker = Faker()
        cls.list_create_post_url = reverse('post-list')
        cls.list_of_update_payloads = [
            cls._post_payload(1),
            cls._post_payload(0),
            cls._post_payload(1),
        ]

    def setUp(self):
        self.authorize_client()
        for post in range(5):
            self._create_post()

    @classmethod
    def _post_payload(cls, status_=0):
        return dict(
            title=cls.faker.catch_phrase(),
            content=cls.faker.text(),
            slug=cls.faker.uri_path(),
            status=status_,
        )

    def _create_post(self):
        payload = self._post_payload()
        self.client.post(self.list_create_post_url, payload)

    def _create_multiple_posts(self, quantity=10):
        for post in range(quantity):
            self._create_post()

    def test__edit_blog_post(self):
        post = Post.objects.all()[3]
        url = reverse('post-detail', kwargs={"pk": post.id})
        for payload in self.list_of_update_payloads:
            self.client.put(url, payload)
        final_state = (
                self.list_of_update_payloads[0] | self.list_of_update_payloads[1] | self.list_of_update_payloads[2]
        )
        post = Post.objects.get(id=post.id)
        self.assertEqual(post.events.count(), len(self.list_of_update_payloads) + 1)
        self.assertEqual(post.events.count(), post.version)
        self.assertEqual(post.title, final_state['title'])
        self.assertEqual(post.content, final_state['content'])
        self.assertEqual(post.slug, final_state['slug'])
        self.assertEqual(post.version, 4)
        self.assertEqual(post.status, 1)

    def test__delete_blog_post(self):
        post = Post.objects.all()[3]
        url = reverse('post-detail', kwargs={"pk": post.id})
        for payload in self.list_of_update_payloads:
            self.client.put(url, payload)
        delete_response = self.client.delete(url)
        self.assertEqual(delete_response.status_code, status.HTTP_204_NO_CONTENT)
        post.refresh_from_db()
        self.assertEqual(post.version, post.events.count())
        self.assertEqual(post.version, len(self.list_of_update_payloads) + 2)
        self.assertEqual(post.deleted, True)

    def test__delete_blog_logs(self):
        post = Post.objects.all()[3]
        url = reverse('post-detail', kwargs={"pk": post.id})
        for payload in self.list_of_update_payloads:
            self.client.put(url, payload)
        url_logs = reverse('post-logs', kwargs={"pk": post.id})
        response = self.client.get(url_logs)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), len(self.list_of_update_payloads) + 1)
