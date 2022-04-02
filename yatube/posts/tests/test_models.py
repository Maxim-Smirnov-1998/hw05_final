from django.test import TestCase

from ..models import Group, Post, User
from .consts import USERNAME


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username=USERNAME)
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовое описание поля текст',
        )

    def test_models_have_correct_object_names(self):
        """Проверяем, что у моделей корректно работает __str__."""
        self.assertEqual(self.group.title, str(self.group))
        self.assertEqual(f'Post {self.post.text[:15]}', str(self.post))

    def test_verbose_name(self):
        """verbose_name в полях совпадает с ожидаемым."""
        field_verboses_group = {
            'title': 'Заголовок',
            'slug': 'Тег',
            'description': 'Описание'
        }
        for field, expected_value in field_verboses_group.items():
            with self.subTest(field=field):
                self.assertEqual(
                    Group._meta.get_field(field).verbose_name, expected_value)
        field_verboses_post = {
            'text': 'Текст поста',
            'pub_date': 'Дата публикации',
            'author': 'Автор',
            'group': 'Группа'
        }
        for field, expected_value in field_verboses_post.items():
            with self.subTest(field=field):
                self.assertEqual(
                    Post._meta.get_field(field).verbose_name, expected_value)

    def test_help_text(self):
        """help_text в полях совпадает с ожидаемым."""
        field_help_text = {
            'group': 'Группа, к которой будет относиться пост',
            'text': 'Введите текст поста'
        }
        for field, expected_value in field_help_text.items():
            with self.subTest(field=field):
                self.assertEqual(
                    Post._meta.get_field(field).help_text, expected_value)
