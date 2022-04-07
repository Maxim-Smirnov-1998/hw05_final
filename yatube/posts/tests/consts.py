from django.urls import reverse

USERNAME = 'TestUser'
USERNAME_2 = 'TestUser_2'
USERNAME_3 = 'TestUser_3'
USERNAME_4 = 'TestUser_4'
SLUG = 'test-slug'
SLUG_2 = 'test_slug_2'
NEXT = '{}?next={}'

TEMPLATE_ERROR_404 = 'core/404.html'

LOGIN_URL = reverse('users:login')
INDEX_URL = reverse('posts:index')
PROFILE_URL = reverse('posts:profile', args=[USERNAME])
PROFILE_URL_2 = reverse('posts:profile', args=[USERNAME_2])
GROUP_LIST_URL = reverse('posts:group_list', args=[SLUG])
POST_CREATE_URL = reverse('posts:post_create')
GROUP_LIST_URL_2 = reverse('posts:group_list', args=[SLUG_2])
POST_CREATE_REDIRECT = NEXT.format(LOGIN_URL, POST_CREATE_URL)
FOLLOW_URL = reverse('posts:follow_index')
PROFILE_FOLLOW = reverse('posts:profile_follow', args=[USERNAME_2])
PROFILE_UNFOLLOW = reverse('posts:profile_unfollow', args=[USERNAME_2])
UNFOLLOW_REDIRECT = NEXT.format(LOGIN_URL, PROFILE_UNFOLLOW)
FOLLOW_REDIRECT = NEXT.format(LOGIN_URL, PROFILE_FOLLOW)

GIF = (
    b'\x47\x49\x46\x38\x39\x61\x02\x00'
    b'\x01\x00\x80\x00\x00\x00\x00\x00'
    b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
    b'\x00\x00\x00\x2C\x00\x00\x00\x00'
    b'\x02\x00\x01\x00\x00\x02\x02\x0C'
    b'\x0A\x00\x3B'
)
