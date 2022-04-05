import tempfile
import shutil

from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.cache import cache
from django.conf import settings
from django.test import TestCase, Client, override_settings
from django.urls import reverse

from ..models import Group, Post, User, Comment, Follow
from .consts import INDEX_URL, PROFILE_URL, GROUP_LIST_URL, USERNAME
from .consts import SLUG, GROUP_LIST_URL_2, SLUG_2, FOLLOW_URL
from .consts import USERNAME_2, USERNAME_3, USERNAME_4, GIF
from .consts import PROFILE_FOLLOW, PROFILE_UNFOLLOW


TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class ViewsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.guest_client = Client()
        cls.user = User.objects.create_user(username=USERNAME)
        cls.user_2 = User.objects.create_user(username=USERNAME_2)
        cls.user_3 = User.objects.create_user(username=USERNAME_3)
        cls.user_4 = User.objects.create_user(username=USERNAME_4)
        cls.authorized_client = Client()
        cls.another_authorized = Client()
        cls.another_authorized_2 = Client()
        cls.authorized_client.force_login(cls.user)
        cls.another_authorized.force_login(cls.user_3)
        cls.another_authorized_2.force_login(cls.user_4)
        cls.image = SimpleUploadedFile(
            name='small.gif',
            content=GIF,
            content_type='image/gif'
        )
        cls.group = Group.objects.create(
            title='Тестовый заголовок',
            slug=SLUG,
            description='Тестовое описание',
        )
        cls.group_2 = Group.objects.create(
            title='Тестовый заголовок',
            slug=SLUG_2,
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            text='Тестовый текст',
            group=cls.group,
            author=cls.user,
            image=cls.image
        )
        cls.comment = Comment.objects.create(
            post=cls.post,
            author=cls.user_3,
            text='Комментарий'
        )
        cls.follow = Follow.objects.create(
            user=cls.user_4,
            author=cls.user
        )
        cls.POST_DETAIL_URL = reverse('posts:post_detail', args=[cls.post.pk])
        cls.POST_EDIT_URL = reverse('posts:post_edit', args=[cls.post.pk])

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def test_show_correct_context(self):
        CASES = [
            (INDEX_URL, self.guest_client, 'page_obj'),
            (GROUP_LIST_URL, self.guest_client, 'page_obj'),
            (PROFILE_URL, self.authorized_client, 'page_obj'),
            (self.POST_DETAIL_URL, self.guest_client, 'post'),
            (FOLLOW_URL, self.another_authorized_2, 'page_obj')
        ]
        for url, client, context in CASES:
            with self.subTest(url=url):
                response = client.get(url)
                post = response.context[context]
                if context == 'page_obj':
                    self.assertEqual(len(post), 1)
                    post = post[0]
                self.assertEqual(post.id, self.post.id)
                self.assertEqual(post.text, self.post.text)
                self.assertEqual(post.group, self.group)
                self.assertEqual(post.author, self.post.author)
                self.assertEqual(post.image, self.post.image)

    def test_cache(self):
        """Данные в кэше хранятся до его обновления/очистки"""
        response = self.guest_client.get(INDEX_URL)
        Post.objects.all().delete()
        self.assertEqual(
            response.content, self.guest_client.get(INDEX_URL).content
        )
        cache.clear()
        self.assertFalse(
            response.content == self.guest_client.get(INDEX_URL).content
        )

    def test_profile_in_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        response = self.authorized_client.get(PROFILE_URL)
        self.assertEqual(response.context['user'], self.post.author)

    def test_group_in_context_group_list(self):
        """Шаблон group_list сформирован с правильным контекстом."""
        response = self.guest_client.get(GROUP_LIST_URL)
        group = response.context['group']
        self.assertEqual(group, self.post.group)
        self.assertEqual(group.slug, self.post.group.slug)
        self.assertEqual(
            group.description,
            self.post.group.description
        )
        self.assertEqual(group.pk, self.post.group.pk)

    def test_group_not_in_context(self):
        CASES = [
            (GROUP_LIST_URL_2, self.another_authorized, 'page_obj'),
            (FOLLOW_URL, self.another_authorized, 'page_obj')
        ]
        for url, client, context in CASES:
            with self.subTest(url=url):
                page = client.get(url).context[context]
                self.assertNotIn(self.post, page)

    def test_profile_follow_unfollow(self):
        """Авторизованный пользователь может подписываться на других"""
        self.authorized_client.get(PROFILE_FOLLOW)
        self.assertEqual(set(Follow.objects.filter(user=self.user)), set(1))

    def test_profile_follow_unfollow(self):
        """Авторизованный пользователь может удалять пользователей"""
        """из подписок."""
        self.authorized_client.get(PROFILE_UNFOLLOW)
        self.assertEqual(set(Follow.objects.filter(user=self.user_3)), set())
        self.assertEqual(set(Follow.objects.filter(user=self.user)), set())

    def test_pages_index_contains_correct_records(self):
        """На страницу выводится корректное кол-во постов"""
        NUMBER_FOR_TEST = 3

        count_posts_on_page = (settings.POSTS_ON_PAGE + NUMBER_FOR_TEST
                               - Post.objects.count()
                               )
        Post.objects.bulk_create(
            Post(text='Тестовый текст',
                 group=self.group,
                 author=self.user
                 ) for i in range(count_posts_on_page)
        )
        CASES = [
            (INDEX_URL, settings.POSTS_ON_PAGE, self.guest_client),
            (GROUP_LIST_URL, settings.POSTS_ON_PAGE, self.guest_client),
            (PROFILE_URL, settings.POSTS_ON_PAGE, self.authorized_client),
            (INDEX_URL + '?page=2', NUMBER_FOR_TEST, self.guest_client),
            (GROUP_LIST_URL + '?page=2', NUMBER_FOR_TEST, self.guest_client),
            (PROFILE_URL + '?page=2', NUMBER_FOR_TEST, self.authorized_client)
        ]
        for url, count_posts, client in CASES:
            with self.subTest(url=url):
                self.assertEqual(
                    len(client.get(url).context['page_obj']),
                    count_posts
                )
