from django.test import TestCase
from django.urls import reverse

from ..urls import app_name

USERNAME = 'TestUser'
SLUG = 'test-slug'
POST_ID = 1
CASES = [
    ('index', '/', []),
    ('group_list', f'/group/{SLUG}/', [SLUG]),
    ('profile', f'/profile/{USERNAME}/', [USERNAME]),
    ('post_detail', f'/posts/{POST_ID}/', [POST_ID]),
    ('post_edit', f'/posts/{POST_ID}/edit/', [POST_ID]),
    ('post_create', '/create/', []),
    ('follow_index', '/follow/', []),
    ('add_comment', f'/posts/{POST_ID}/comment/', [POST_ID]),
    ('profile_follow', f'/profile/{USERNAME}/follow/', [USERNAME]),
    ('profile_unfollow', f'/profile/{USERNAME}/unfollow/', [USERNAME])
]


class ViewsTests(TestCase):
    def test_urls(self):

        for name, expected_urls, arguments in CASES:
            with self.subTest(expected_url=expected_urls):
                self.assertEqual(reverse(
                    f'{app_name}:{name}', args=arguments),
                    expected_urls
                )
