import shutil
import time
import tempfile
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth import get_user_model
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django import forms
from posts.models import Post, Group, Follow
from django.core.cache import cache

User = get_user_model()

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class TaskPagesTests(TestCase):
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

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        cache.clear()
        self.authorized_client = Client()
        self.guest_client = Client()
        self.authorized_client_user = Client()
        self.user = User.objects.create_user(username='Petr')
        self.authorized_client.force_login(TaskPagesTests.user)
        self.authorized_client_user.force_login(self.user)
        self.group_2 = Group.objects.create(
            title='Тестовая группа_2',
            slug='Group_test_2',
            description='Тестовое описание',
        )
        self.post_2 = Post.objects.create(
            text='Тестовый текст_2',
            author=TaskPagesTests.user,
            group=self.group_2
        )
        time.sleep(0.001)

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_pages_names = {
            'posts/index.html': reverse('posts:main_page'),
            'posts/group_list.html':
            reverse('posts:group_list',
                    kwargs={'slug': TaskPagesTests.group.slug}),
            'posts/profile.html':
            reverse('posts:profile',
                    kwargs={'username': TaskPagesTests.user}),
            'posts/post_detail.html': (
                reverse('posts:post_detail',
                        kwargs={'post_id': TaskPagesTests.post.id})),
            'posts/create_post.html': reverse('posts:post_edit', kwargs={
                'post_id': TaskPagesTests.post.id})
        }
        for template, reverse_name in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)
        response_create = self.authorized_client.get(
            reverse('posts:post_create'))
        self.assertTemplateUsed(response_create, 'posts/create_post.html')

    def test_main_page_page_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:main_page'))
        first_object = response.context['page_obj'][1]
        posts_amount = len(response.context['page_obj'])
        task_text_0 = first_object.text
        task_group_0 = first_object.group.title
        task_author_0 = first_object.author.username
        self.assertEqual(task_text_0, 'Тестовый текст')
        self.assertEqual(task_group_0, 'Тестовая группа')
        self.assertEqual(task_author_0, 'Ivan')
        self.assertEqual(posts_amount, 2)

    def test_group_list_page_show_correct_context(self):
        """Шаблон group_list сформирован с правильным кол-вом постов группы,
        в шаблон не попала чужая группа"""
        response = self.authorized_client.get(
            reverse('posts:group_list',
                    kwargs={'slug': TaskPagesTests.group.slug}))
        first_object = response.context['page_obj'][0]
        posts_amount = len(response.context['page_obj'])
        task_text_0 = first_object.text
        task_group_0 = first_object.group.title
        task_author_0 = first_object.author.username
        self.assertEqual(task_text_0, 'Тестовый текст')
        self.assertEqual(task_group_0, 'Тестовая группа')
        self.assertEqual(task_author_0, 'Ivan')
        self.assertEqual(posts_amount, 1)
        self.assertNotContains(response, 'Тестовый текст_2')
        self.assertNotEqual(task_group_0, 'Тестовая группа_2')

    def test_profile_page_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:profile', kwargs={'username': TaskPagesTests.user}))
        first_object = response.context['page_obj'][1]
        posts_amount = Post.objects.filter(author=TaskPagesTests.user).count()
        task_text_0 = first_object.text
        task_group_0 = first_object.group.title
        task_author_0 = first_object.author.username
        self.assertEqual(task_text_0, 'Тестовый текст')
        self.assertEqual(task_group_0, 'Тестовая группа')
        self.assertEqual(task_author_0, 'Ivan')
        self.assertEqual(posts_amount, 2)

    def test_post_detail_pages_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = (self.authorized_client.
                    get(reverse('posts:post_detail',
                        kwargs={'post_id': self.post_2.id})))
        self.assertEqual(response.context.get('post').text, 'Тестовый текст_2')

    def test_create_page_show_correct_context(self):
        """Шаблон home сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:post_create'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.models.ModelChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_edit_page_show_correct_context(self):
        """Шаблон home сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:post_edit',
                    kwargs={'post_id': TaskPagesTests.post.id}))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.models.ModelChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)
        self.assertContains(response, 'Тестовый текст')

    def test_guest_access_create_edit_pages(self):
        adresses = {self.guest_client.get(
            reverse('posts:post_create')): '/auth/login/?next=/create/',
            self.guest_client.get(reverse('posts:post_edit',
                                  kwargs={'post_id': TaskPagesTests.post.id})):
            '/auth/login/?next=/posts/1/edit/'}
        for response, answer in adresses.items():
            with self.subTest(response=response):
                self.assertRedirects(response, answer)

    def test_user_access_edit_page(self):
        response = self.authorized_client_user.get(
            reverse('posts:post_edit',
                    kwargs={'post_id': TaskPagesTests.post.id}))
        redirect_page = reverse('posts:post_detail',
                                kwargs={'post_id': TaskPagesTests.post.id})
        self.assertRedirects(response, redirect_page)

    def test_img_context_correct_check(self):
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='test.gif',
            content=small_gif,
            content_type='image/gif'
        )
        self.group_3 = Group.objects.create(
            title='Тестовая группа_3',
            slug='Group_test_3',
            description='Тестовое описание',
        )
        self.post_3 = Post.objects.create(
            text='Тестовый текст_3',
            author=TaskPagesTests.user,
            image=uploaded,
            group=self.group_3
        )
        response_index = self.authorized_client.get(
            reverse('posts:main_page'))
        first_object_index = response_index.context['page_obj'][0]
        task_img_index = first_object_index.image
        response_profile = self.authorized_client.get(
            reverse('posts:profile', kwargs={'username': TaskPagesTests.user}))
        first_object_profile = response_profile.context['page_obj'][0]
        task_img_profile = first_object_profile.image
        response_group = self.authorized_client.get(
            reverse('posts:group_list', kwargs={'slug': self.group_3.slug}))
        first_object_group = response_group.context['page_obj'][0]
        task_img_group = first_object_group.image
        response_post = self.authorized_client.get(
            reverse('posts:post_detail', kwargs={'post_id': self.post_3.id}))
        task_img_post = response_post.context['post'].image
        images = [task_img_index,
                  task_img_profile, task_img_group, task_img_post]
        for img in images:
            self.assertEqual(img, 'posts/test.gif')

    def test_guest_access_comment(self):
        response = self.guest_client.get(
            reverse('posts:add_comment',
                    kwargs={'post_id': TaskPagesTests.post.id}))
        self.assertRedirects(response, '/auth/login/?next=/posts/1/comment/')

    def test_new_comment_correct_display(self):
        form_data = {
            'text': 'Привет',
            'author': TaskPagesTests.user,
            'post': TaskPagesTests.post
        }
        self.authorized_client.post(
            reverse('posts:add_comment',
                    kwargs={'post_id': TaskPagesTests.post.id}),
            data=form_data,
            follow=True
        )
        response = self.authorized_client.get(
            reverse('posts:post_detail',
                    kwargs={'post_id': TaskPagesTests.post.id}))
        self.assertEqual(response.context['comments'][0].text, 'Привет')

    def test_404_template_custom_display(self):
        response = self.authorized_client.get('unforeknowable/')
        self.assertTemplateUsed(response, 'core/404.html')

    def test_auth_user_following(self):
        self.user = User.objects.create_user(username='Gena')
        self.post = Post.objects.create(
            text='Лайк, подписка',
            author=self.user,
        )
        self.authorized_client.post(
            reverse('posts:profile_follow',
                    kwargs={'username': self.user}))
        following = Follow.objects.filter(user=TaskPagesTests.user).first()
        following_name = following.author.username
        self.assertEquals(following_name, 'Gena')
        self.authorized_client.post(
            reverse('posts:profile_unfollow',
                    kwargs={'username': self.user}))
        following_number = len(Follow.objects.filter(author=self.user))
        self.assertEquals(following_number, 0)

    def test_post_following_display(self):
        self.user = User.objects.create_user(username='Gena')
        self.post = Post.objects.create(
            text='Лайк, подписка',
            author=self.user,
        )
        self.authorized_client.post(
            reverse('posts:profile_follow',
                    kwargs={'username': self.user}))
        response_follower = self.authorized_client.get(
            reverse('posts:follow_index'))
        response_nonfollower = self.authorized_client_user.get(
            reverse('posts:follow_index'))
        self.assertContains(response_follower, 'Лайк, подписка')
        self.assertNotContains(response_nonfollower, 'Лайк, подписка')


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Ivan')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Group_test',
            description='Тестовое описание',
        )
        texts_num = 13
        for text_num in range(texts_num):
            Post.objects.create(
                text='Test text № %s' % text_num,
                author=cls.user, group=cls.group)

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(PaginatorViewsTest.user)

    def test_index_page_contains_ten_records(self):
        cache.clear()
        response = self.authorized_client.get(reverse('posts:main_page'))
        self.assertEqual(len(response.context['page_obj']), 10)

    def test_second_index_page_contains_three_records(self):
        response = self.authorized_client.get(
            reverse('posts:main_page') + '?page=2')
        self.assertEqual(len(response.context['page_obj']), 3)

    def test_group_page_contains_ten_records(self):
        response = self.authorized_client.get(
            reverse('posts:group_list',
                    kwargs={'slug': PaginatorViewsTest.group.slug}))
        self.assertEqual(len(response.context['page_obj']), 10)

    def test_second_group_page_contains_three_records(self):
        response = self.authorized_client.get(
            reverse('posts:group_list',
                    kwargs={'slug':
                            PaginatorViewsTest.group.slug}) + '?page=2')
        self.assertEqual(len(response.context['page_obj']), 3)

    def test_profile_page_contains_ten_records(self):
        response = self.authorized_client.get(
            reverse('posts:profile',
                    kwargs={'username': PaginatorViewsTest.user}))
        self.assertEqual(len(response.context['page_obj']), 10)

    def test_profile_group_page_contains_three_records(self):
        response = self.authorized_client.get(
            reverse('posts:profile',
                    kwargs={'username': PaginatorViewsTest.user}) + '?page=2')
        self.assertEqual(len(response.context['page_obj']), 3)
