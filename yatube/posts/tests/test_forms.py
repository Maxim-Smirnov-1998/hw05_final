import tempfile
import shutil

from django.test import TestCase, Client, override_settings
from django.urls import reverse
from django.conf import settings
from django import forms
from django.core.files.uploadedfile import SimpleUploadedFile

from ..models import Group, Post, User
from .consts import PROFILE_URL, POST_CREATE_URL, USERNAME, SLUG


TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class FormsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.guest_client = Client()
        cls.user = User.objects.create_user(username=USERNAME)
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
        cls.gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.image = SimpleUploadedFile(
            name='small.gif',
            content=cls.gif,
            content_type='image/gif'
        )
        cls.group = Group.objects.create(
            title='Тестовый заголовок',
            slug=SLUG,
            description='Тестовое описание',
        )

        cls.group_2 = Group.objects.create(
            title='Тестовый заголовок для проверки',
            slug='test_slug_2',
            description='Тестовое описание для проверки',
        )

        cls.post = Post.objects.create(
            text='Тестовый текст',
            group=cls.group,
            author=cls.user,
            image=cls.image
        )

        cls.POST_DETAIL_URL = reverse('posts:post_detail', args=[cls.post.id])
        cls.POST_EDIT_URL = reverse('posts:post_edit', args=[cls.post.id])

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def test_create_post(self):
        """Валидная форма создает запись в Post."""
        posts = set(Post.objects.all())

        form_data = {
            'text': 'Тестовый текст',
            'group': self.group.pk,
            'image': self.post.image,
        }
        response = self.authorized_client.post(
            POST_CREATE_URL,
            data=form_data,
            follow=True
        )
        posts = set(Post.objects.all()) - posts
        self.assertEqual(len(posts), 1)
        post = posts.pop()
        self.assertEqual(form_data['text'], post.text)
        self.assertEqual(form_data['group'], post.group.pk)
        self.assertEqual(
            form_data['image'].name,
            'posts/' + self.image.name
        )
        self.assertEqual(post.author, self.user)
        self.assertRedirects(response, PROFILE_URL)

    def test_create_post_show_correct_fields(self):
        response = self.authorized_client.get(POST_CREATE_URL)
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)

    def test_edit_post(self):
        """Валидная форма редактирует запись в Post."""
        form_data = {
            'text': 'Тестовый текст для проверки',
            'group': self.group_2.pk,
        }
        response = self.authorized_client.post(
            self.POST_EDIT_URL,
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, self.POST_DETAIL_URL)
        post = response.context['post']
        self.assertEqual(form_data['text'], post.text)
        self.assertEqual(form_data['group'], post.group.pk)
        self.assertEqual(post.author, self.post.author)
