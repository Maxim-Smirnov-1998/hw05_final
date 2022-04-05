from django.test import TestCase
from django.urls import reverse
from ..urls import app_name
from .consts import URLS


class ViewsTests(TestCase):
    def test_urls(self):
        for name, expected_urls, arguments in URLS:
            with self.subTest(expected_url=expected_urls):
                self.assertEqual(reverse
                                 (app_name + ':' + name, args=arguments),
                                 expected_urls
                                 )
