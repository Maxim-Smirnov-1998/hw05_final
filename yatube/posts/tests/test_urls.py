from django.test import TestCase, Client
from django.urls import reverse

from ..models import Group, Post, User
from .consts import INDEX_URL, PROFILE_URL_2, GROUP_LIST_URL
from .consts import POST_CREATE_URL, USERNAME_2, SLUG, POST_CREATE_REDIRECT
from .consts import LOGIN_URL, NEXT, FOLLOW_URL, PROFILE_FOLLOW
from .consts import TEMPLATE_ERROR_404, PROFILE_UNFOLLOW
from .consts import FOLLOW_REDIRECT, UNFOLLOW_REDIRECT


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.guest = Client(follow=True)
        cls.user = User.objects.create_user(username=USERNAME_2)
        cls.author = Client()
        cls.author.force_login(cls.user)
        cls.user_2 = User.objects.create_user(username='not_author')
        cls.another = Client()
        cls.another.force_login(cls.user_2)
        cls.group = Group.objects.create(
            title='Тестовый заголовок',
            slug=SLUG,
            description='Тестовое описание'
        )
        cls.post = Post.objects.create(
            text='Тестовый текст',
            group=cls.group,
            author=cls.user
        )
        cls.POST_DETAIL_URL = reverse('posts:post_detail', args=[cls.post.pk])
        cls.POST_EDIT_URL = reverse('posts:post_edit', args=[cls.post.pk])
        cls.POST_EDIT_REDIRECT = NEXT.format(LOGIN_URL, cls.POST_EDIT_URL)

    def test_urls_status_code(self):
        """Код запроса соответствупет ожидаемому."""
        CASES = [
            (INDEX_URL, self.guest, 200),
            (GROUP_LIST_URL, self.author, 200),
            (PROFILE_URL_2, self.author, 200),
            (self.POST_DETAIL_URL, self.author, 200),
            (self.POST_EDIT_URL, self.author, 200),
            (POST_CREATE_URL, self.author, 200),
            ('/unexisting_page/', self.author, 404),
            (self.POST_EDIT_URL, self.another, 302),
            (POST_CREATE_URL, self.guest, 302),
            (self.POST_EDIT_URL, self.guest, 302),
            (FOLLOW_URL, self.another, 200),
            (PROFILE_FOLLOW, self.another, 302),
            (PROFILE_UNFOLLOW, self.another, 302),
            (FOLLOW_URL, self.guest, 302),
            (PROFILE_FOLLOW, self.guest, 302),
            (PROFILE_UNFOLLOW, self.guest, 302),
            (PROFILE_FOLLOW, self.author, 302),
            (PROFILE_UNFOLLOW, self.author, 302),
            (FOLLOW_URL, self.author, 200)
        ]
        for url, client, expected in CASES:
            with self.subTest(url=url, expected=expected, client=client):
                self.assertEqual(
                    client.get(url).status_code,
                    expected
                )

    def test_urls_redirect(self):
        REDIRECT_TESTS = [
            (self.POST_EDIT_URL, self.POST_DETAIL_URL, self.another),
            (POST_CREATE_URL, POST_CREATE_REDIRECT, self.guest),
            (self.POST_EDIT_URL, self.POST_EDIT_REDIRECT, self.guest),
            (PROFILE_FOLLOW, PROFILE_URL_2, self.another),
            (PROFILE_UNFOLLOW, PROFILE_URL_2, self.another),
            (PROFILE_FOLLOW, FOLLOW_REDIRECT, self.guest),
            (PROFILE_UNFOLLOW, UNFOLLOW_REDIRECT, self.guest),
            (PROFILE_FOLLOW, PROFILE_URL_2, self.author),
            (PROFILE_UNFOLLOW, PROFILE_URL_2, self.author)
        ]
        for url, redirect, client in REDIRECT_TESTS:
            with self.subTest(url=url, redirect=redirect):
                self.assertRedirects(client.get(url), redirect)

    def test_urls_templates(self):
        TEMPLATE_TESTS = [
            (INDEX_URL, self.guest, 'posts/index.html'),
            (GROUP_LIST_URL, self.author, 'posts/group_list.html'),
            (PROFILE_URL_2, self.author, 'posts/profile.html'),
            (self.POST_DETAIL_URL, self.author, 'posts/post_detail.html'),
            (self.POST_EDIT_URL, self.author, 'posts/create_post.html'),
            (POST_CREATE_URL, self.author, 'posts/create_post.html'),
            ('/unexisting_page/', self.author, TEMPLATE_ERROR_404),
            (FOLLOW_URL, self.another, 'posts/follow.html'),
        ]
        for url, client, template in TEMPLATE_TESTS:
            with self.subTest(url=url):
                self.assertTemplateUsed(client.get(url), template)
