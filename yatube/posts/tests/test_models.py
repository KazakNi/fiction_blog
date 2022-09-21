from django.contrib.auth import get_user_model
from django.test import TestCase

from posts.models import Group, Post

User = get_user_model()


class PostModelTest(TestCase):
    STR_LETTERS_NUMBER = 15

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Group_test',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
        )

    def test_models_correct_object_names(self):
        post = PostModelTest.post
        group = PostModelTest.group
        expected_object_name_post = post.text[
            :PostModelTest.STR_LETTERS_NUMBER]
        expected_object_name_group = group.title

        objects_str = {
            expected_object_name_post: str(post),
            expected_object_name_group: str(group)
        }
        for obj_str, expected_value in objects_str.items():
            with self.subTest(obj_str=obj_str):
                self.assertEqual(obj_str, str(expected_value))
