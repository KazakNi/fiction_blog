from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from posts.models import Group, Post
from http import HTTPStatus
from django.core.cache import cache

cache.clear()

User = get_user_model()


class StaticURLTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_homepage(self):
        response = self.guest_client.get('/')
        self.assertEqual(response.status_code, HTTPStatus.OK)


class TaskURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Ivan')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Group_test',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            text='Тестовый текст',
            author=cls.user,
            group=cls.group
        )

    def setUp(self):
        cache.clear()
        self.guest_client = Client()
        self.user = User.objects.create_user(username='Petr')
        self.authorized_client_author = Client()
        self.authorized_client_user = Client()
        self.authorized_client_author.force_login(TaskURLTests.user)
        self.authorized_client_user.force_login(self.user)

    def test_urls_unauth_users_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        # Шаблоны по адресам
        templates_url_names = {
            'posts/index.html': '/',
            'posts/group_list.html': f'/group/{TaskURLTests.post.group.slug}/',
            'posts/profile.html': f'/profile/{TaskURLTests.user}/',
            'posts/post_detail.html': f'/posts/{TaskURLTests.post.id}/',
        }
        for template, address in templates_url_names.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertTemplateUsed(response, template)

    def test_non_existing_page(self):
        response = self.guest_client.get('/nevermind/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_auth_user_post_creating(self):
        response = self.authorized_client_user.get('/create/')
        self.assertTemplateUsed(response, 'posts/create_post.html')

    def test_auth_user_post_editing_by_author(self):
        response = self.authorized_client_author.get(
            f'/posts/{TaskURLTests.post.id}/edit/')
        self.assertTemplateUsed(response, 'posts/create_post.html')

    def test_auth_user_post_editing_by_non_author(self):
        response = self.authorized_client_user.get(
            f'/posts/{TaskURLTests.post.id}/edit/')
        self.assertRedirects(response, f'/posts/{TaskURLTests.post.id}/')
