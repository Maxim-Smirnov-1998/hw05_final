from django.urls import reverse

USERNAME = 'TestUser'
USERNAME_2 = 'TestUser_2'
USERNAME_3 = 'TestUser_3'
USERNAME_4 = 'TestUser_4'
SLUG = 'test-slug'
SLUG_2 = 'test_slug_2'
CONST = '{}?next={}'

LOGIN_URL = reverse('users:login')
INDEX_URL = reverse('posts:index')
PROFILE_URL = reverse('posts:profile', args=[USERNAME])
GROUP_LIST_URL = reverse('posts:group_list', args=[SLUG])
POST_CREATE_URL = reverse('posts:post_create')
GROUP_LIST_URL_2 = reverse('posts:group_list', args=[SLUG_2])
POST_CREATE_REDIRECT = CONST.format(LOGIN_URL, POST_CREATE_URL)
FOLLOW_URL = reverse('posts:follow_index')
