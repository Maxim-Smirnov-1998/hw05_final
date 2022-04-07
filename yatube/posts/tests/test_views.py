import tempfile
import shutil

from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.cache import cache
from django.conf import settings
from django.test import TestCase, Client, override_settings
from django.urls import reverse

from ..models import Group, Post, User, Comment, Follow


TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)

USERNAME = 'TestUser'
USERNAME_2 = 'TestUser_2'
USERNAME_3 = 'TestUser_3'
USERNAME_4 = 'TestUser_4'
SLUG = 'test-slug'
SLUG_2 = 'test_slug_2'

INDEX_URL = reverse('posts:index')
PROFILE_URL = reverse('posts:profile', args=[USERNAME])
GROUP_LIST_URL = reverse('posts:group_list', args=[SLUG])
GROUP_LIST_URL_2 = reverse('posts:group_list', args=[SLUG_2])
FOLLOW_URL = reverse('posts:follow_index')
PROFILE_FOLLOW = reverse('posts:profile_follow', args=[USERNAME_2])
PROFILE_UNFOLLOW = reverse('posts:profile_unfollow', args=[USERNAME_2])

GIF = (
    b'\x47\x49\x46\x38\x39\x61\x02\x00'
    b'\x01\x00\x80\x00\x00\x00\x00\x00'
    b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
    b'\x00\x00\x00\x2C\x00\x00\x00\x00'
    b'\x02\x00\x01\x00\x00\x02\x02\x0C'
    b'\x0A\x00\x3B'
)


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
        self.assertNotEqual(
            response.content, self.guest_client.get(INDEX_URL).content
        )

    def test_profile_in_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        response = self.authorized_client.get(PROFILE_URL)
        self.assertEqual(response.context['author'], self.post.author)

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

    def test_post_not_in_context(self):
        CASES = [
            (GROUP_LIST_URL_2, self.another_authorized, 'page_obj'),
            (FOLLOW_URL, self.another_authorized, 'page_obj')
        ]
        for url, client, context in CASES:
            with self.subTest(url=url):
                page = client.get(url).context[context]
                self.assertNotIn(self.post, page)

    def test_profile_follow_follow(self):
        """Авторизованный пользователь может подписываться на других"""
        self.authorized_client.get(PROFILE_FOLLOW)
        self.assertTrue(Follow.objects.filter(
            author__username=USERNAME_2, user=self.user
        ).exists())

    def test_profile_follow_unfollow(self):
        """Авторизованный пользователь может удалять пользователей"""
        """из подписок."""
        self.authorized_client.get(PROFILE_UNFOLLOW)
        self.assertFalse(Follow.objects.filter(
            author__username=USERNAME_2, user=self.user
        ).exists())

    def test_pages_index_contains_correct_records(self):
        """На страницу выводится корректное кол-во постов"""
        Post.objects.all().delete()
        NUMBER_FOR_TEST = 3

        count_posts = settings.POSTS_ON_PAGE + NUMBER_FOR_TEST
        Post.objects.bulk_create(
            Post(text='Тестовый текст',
                 group=self.group,
                 author=self.user
                 ) for i in range(count_posts)
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
                print(len(client.get(url).context['page_obj']))
                self.assertEqual(
                    len(client.get(url).context['page_obj']),
                    count_posts
                )
