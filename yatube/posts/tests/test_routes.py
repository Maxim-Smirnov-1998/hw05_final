from django.test import TestCase
from django.urls import reverse
from ..urls import app_name


class ViewsTests(TestCase):
    def test_urls(self):
        POST_ID = 1
        USERNAME = 'TestUser'
        SLUG = 'test-slug'
        urls = [
            (':index', '/', []),
            (':group_list', f'/group/{SLUG}/', [SLUG]),
            (':profile', f'/profile/{USERNAME}/', [USERNAME]),
            (':post_detail', f'/posts/{POST_ID}/', [POST_ID]),
            (':post_edit', f'/posts/{POST_ID}/edit/', [POST_ID]),
            (':post_create', '/create/', []),
            (':follow_index', '/follow/', []),
            (':add_comment', f'/posts/{POST_ID}/comment/', [POST_ID]),
            (':profile_follow', f'/profile/{USERNAME}/follow/', [USERNAME]),
            (':profile_unfollow', f'/profile/{USERNAME}/unfollow/', [USERNAME])
        ]
        for name, expected_urls, arguments in urls:
            with self.subTest(expected_url=expected_urls):
                self.assertEqual(reverse(app_name + name, args=arguments),
                                 expected_urls
                                 )
