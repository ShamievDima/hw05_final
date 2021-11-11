from http import HTTPStatus
from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse

from posts.models import Post, Group

User = get_user_model()


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='TestUser')
        cls.group = Group.objects.create(
            title='test-title',
            slug='test-slug',
            description='test-descrp',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='test-text',
            group=cls.group,
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_guest_client_url_exists_at_desired_location(self):
        """Проверка страниц сайта на доступ неавторизованному пользователю"""
        status_code_url_names = {
            '/': HTTPStatus.OK,
            f'/group/{self.group.slug}/': HTTPStatus.OK,
            f'/profile/{self.user.username}/': HTTPStatus.OK,
            f'/posts/{self.post.pk}/': HTTPStatus.OK,
            '/unexisting_page/': HTTPStatus.NOT_FOUND,
        }
        for adress, http_status in status_code_url_names.items():
            with self.subTest(adress=adress):
                response = self.client.get(adress)
                self.assertEqual(response.status_code, http_status)

    def test_authorized_client_url_exists_at_desired_location(self):
        """Проверка страниц сайта на доступ авторизованному пользователю"""
        status_code_url_names = {
            '/create/': HTTPStatus.OK,
            f'/posts/{self.post.id}/edit/': HTTPStatus.OK,
        }
        for adress, http_status in status_code_url_names.items():
            with self.subTest(adress=adress):
                response = self.authorized_client.get(adress)
                self.assertEqual(response.status_code, http_status)

    def test_post_create_url_redirect_anonymous_on_admin_login(self):
        """Страница /create/ перенаправит анонимного пользователя
        на страницу логина.
        """
        response = self.client.get('/create/', follow=True)
        self.assertRedirects(
            response, '/auth/login/?next=/create/')

    def test_post_edit_url_redirect_anonymous_on_admin_login(self):
        """Страница /posts/post_id/edit/ перенаправит анонимного
        пользователя на страницу логина.
        """
        response = self.client.get(
            reverse(
                'posts:post_edit', kwargs={'post_id': f'{self.post.pk}'}
            ), follow=True
        )
        '''response = self.client.get(
            f'/posts/{self.post.pk}/edit/', follow=True
        )'''
        self.assertRedirects(
            response, (
                f'/auth/login/?next=/posts/{self.post.pk}/edit/'
            )
        )

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            '/': 'posts/index.html',
            f'/group/{self.group.slug}/': 'posts/group_list.html',
            f'/profile/{self.user.username}/': 'posts/profile.html',
            f'/posts/{self.post.pk}/': 'posts/post_detail.html',
            '/create/': 'posts/create.html',
            f'/posts/{self.post.pk}/edit/': 'posts/create.html',
        }
        for url, template in templates_url_names.items():
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertTemplateUsed(response, template)
