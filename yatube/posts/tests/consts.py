from django.urls import reverse

USERNAME = 'TestUser'
USERNAME_2 = 'TestUser_2'
USERNAME_3 = 'TestUser_3'
USERNAME_4 = 'TestUser_4'
SLUG = 'test-slug'
SLUG_2 = 'test_slug_2'
CONST = '{}?next={}'
POST_ID = 1


LOGIN_URL = reverse('users:login')
INDEX_URL = reverse('posts:index')
PROFILE_URL = reverse('posts:profile', args=[USERNAME])
GROUP_LIST_URL = reverse('posts:group_list', args=[SLUG])
POST_CREATE_URL = reverse('posts:post_create')
GROUP_LIST_URL_2 = reverse('posts:group_list', args=[SLUG_2])
POST_CREATE_REDIRECT = CONST.format(LOGIN_URL, POST_CREATE_URL)
FOLLOW_URL = reverse('posts:follow_index')
PROFILE_FOLLOW = reverse('posts:profile_follow', args=[USERNAME_2])
PROFILE_UNFOLLOW = reverse('posts:profile_unfollow', args=[USERNAME_2])

URLS = [
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

GIF = (
    b'\x47\x49\x46\x38\x39\x61\x02\x00'
    b'\x01\x00\x80\x00\x00\x00\x00\x00'
    b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
    b'\x00\x00\x00\x2C\x00\x00\x00\x00'
    b'\x02\x00\x01\x00\x00\x02\x02\x0C'
    b'\x0A\x00\x3B'
)
