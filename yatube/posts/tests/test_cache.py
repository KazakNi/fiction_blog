from django.test import Client, TestCase
from django.contrib.auth import get_user_model
from posts.models import Post, Group
from django.urls import reverse
import time

User = get_user_model()


class CachePageTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Ivan')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Group_test',
            description='Тестовое описание',)

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(CachePageTest.user)

    def test_cache_correct_work(self):
        self.post = Post.objects.create(
            text='Тестовый текст',
            author=CachePageTest.user,
            group=CachePageTest.group
        )
        cache_1 = self.authorized_client.get(
            reverse('posts:main_page')).content
        instance = Post.objects.get(pk=1)
        instance.delete()
        time.sleep(5)
        cache_2 = self.authorized_client.get(
            reverse('posts:main_page')).content
        self.assertEquals(cache_1, cache_2, True)
        time.sleep(16)
        cache_3 = self.authorized_client.get(
            reverse('posts:main_page')).content
        self.assertNotEquals(cache_1, cache_3, True)
