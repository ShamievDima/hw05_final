import shutil
import tempfile

import datetime as dt

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django import forms
from django.core.cache import cache

from yatube.settings import PAGINATOR_SETINGS

from posts.models import Post, Group, Follow

User = get_user_model()
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


class PostViewsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='TestUser')
        cls.group = Group.objects.create(
            title='test-title',
            slug='test-slug',
            description='test-descrp',
        )
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='test-text',
            group=cls.group,
            image=uploaded,
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def compare_objects(self, post):
        self.assertEqual(post.text, f'{self.post.text}')
        self.assertEqual(post.author.username, self.user.username)
        self.assertEqual(post.group, self.group)
        self.assertEqual(post.image, self.post.image)

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_page_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse(
                'posts:group_posts', kwargs={'slug': f'{self.group.slug}'}):
            'posts/group_list.html',
            reverse(
                'posts:profile', kwargs={'username': f'{self.user.username}'}):
            'posts/profile.html',
            reverse(
                'posts:post_detail', kwargs={'post_id': f'{self.post.pk}'}):
            'posts/post_detail.html',
            reverse('posts:post_create'): 'posts/create.html',
            reverse(
                'posts:post_edit', kwargs={'post_id': f'{self.post.pk}'}):
            'posts/create.html',
        }
        for reverse_name, template in templates_page_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_page_show_correct_context(self):
        """Шаблон index.html сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:index'))
        first_object = response.context['page_obj'][0]
        task_id_0 = first_object.pk
        task_pub_date_0 = first_object.pub_date.today().strftime('%d/%m/%Y')
        self.assertEqual(
            task_pub_date_0, dt.datetime.now().strftime('%d/%m/%Y')
        )
        self.assertEqual(task_id_0, self.post.pk)
        self.compare_objects(PostViewsTests.post)

    def test_group_list_page_show_correct_context(self):
        """Шаблон group_list.html сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:group_posts', kwargs={'slug': f'{self.group.slug}'})
        )
        first_object_p = response.context['page_obj'][0]
        first_object_g = response.context['group']
        task_id_0 = first_object_p.pk
        task_pub_date_0 = first_object_p.pub_date.today().strftime('%d/%m/%Y')
        task_title_0 = first_object_g.title
        task_description_0 = first_object_g.description
        self.assertEqual(
            task_pub_date_0, dt.datetime.now().strftime('%d/%m/%Y')
        )
        self.assertEqual(task_title_0, f'{self.group.title}')
        self.assertEqual(task_description_0, f'{self.group.description}')
        self.assertEqual(task_id_0, self.post.pk)
        self.compare_objects(PostViewsTests.post)

    def test_profile_page_show_correct_context(self):
        """Шаблон profile.html сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse(
                'posts:profile', kwargs={'username': f'{self.user.username}'}
            )
        )
        first_object_p = response.context['page_obj'][0]
        first_object_u = response.context['author']
        task_id_0 = first_object_p.pk
        task_pub_date_0 = first_object_p.pub_date.today().strftime('%d/%m/%Y')
        task_username_0 = first_object_u.username
        self.assertEqual(
            task_pub_date_0, dt.datetime.now().strftime('%d/%m/%Y')
        )
        self.assertEqual(task_username_0, f'{self.user.username}')
        self.assertEqual(task_id_0, self.post.pk)
        self.compare_objects(PostViewsTests.post)

    def test_post_detail_page_show_correct_context(self):
        """Шаблон post_detail.html сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:post_detail', kwargs={'post_id': f'{self.post.pk}'})
        )
        first_object = response.context['post']
        task_pub_date_0 = first_object.pub_date.today().strftime('%d/%m/%Y')
        self.assertEqual(
            task_pub_date_0, dt.datetime.now().strftime('%d/%m/%Y')
        )
        self.compare_objects(PostViewsTests.post)

    def test_create_page_show_correct_context(self):
        """Шаблон create.html сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:post_create'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_edit_page_show_correct_context(self):
        """Шаблон post_edit сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:post_edit', kwargs={'post_id': f'{self.post.pk}'})
        )
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_index_page_contains_records(self):
        """Количество постов на главной странице соответствует ожиданиям"""
        for i in range(12):
            Post.objects.create(
                text=f'Testtext_{i}',
                author=self.user,
                group=self.group,
            )
        response = self.client.get(reverse('posts:index'))
        self.assertEqual(
            len(response.context['page_obj']),
            PAGINATOR_SETINGS['PAGE_SIZE']
        )
        response = self.client.get(
            reverse('posts:index') + '?page=2'
        )
        self.assertEqual(len(response.context['page_obj']), 3)

    def test_group_posts_page_contains_records(self):
        """Количество постов на странице группы соответствует ожиданиям"""
        for i in range(12):
            Post.objects.create(
                text=f'Testtext_{i}',
                author=self.user,
                group=self.group,
            )
        response = self.client.get(
            reverse('posts:group_posts', kwargs={'slug': f'{self.group.slug}'})
        )
        self.assertEqual(
            len(response.context['page_obj']),
            PAGINATOR_SETINGS['PAGE_SIZE']
        )
        response = self.client.get(
            reverse(
                'posts:group_posts', kwargs={'slug': f'{self.group.slug}'}
            ) + '?page=2'
        )
        self.assertEqual(len(response.context['page_obj']), 3)

    def test_profile_page_contains_records(self):
        """Количество постов на странице пользователя соответствует
        ожиданиям"""
        for i in range(12):
            Post.objects.create(
                text=f'Testtext_{i}',
                author=self.user,
                group=self.group,
            )
        response = self.client.get(
            reverse(
                'posts:profile', kwargs={'username': f'{self.user.username}'}
            )
        )
        self.assertEqual(
            len(response.context['page_obj']),
            PAGINATOR_SETINGS['PAGE_SIZE']
        )
        response = self.client.get(
            reverse(
                'posts:profile', kwargs={'username': f'{self.user.username}'}
            ) + '?page=2'
        )
        self.assertEqual(len(response.context['page_obj']), 3)

    def test_index_post_view(self):
        """На главной странице отображаются посты."""
        group_posts = PostViewsTests.group
        new_test_post = Post.objects.create(
            author=self.user,
            text='Новое тестовое сообщение',
            group=group_posts,
        )
        response = self.authorized_client.get(reverse('posts:index'))
        first_object = response.context['page_obj'][0]
        self.assertEqual(new_test_post, first_object)

    def test_post_group_view(self):
        """На странице группы отображаются посты."""
        group_posts = PostViewsTests.group
        new_test_post = Post.objects.create(
            author=self.user,
            text='Новое тестовое сообщение',
            group=group_posts,
        )
        response = self.authorized_client.get(
            reverse('posts:group_posts', kwargs={'slug': f'{self.group.slug}'})
        )
        first_object = response.context['page_obj'][0]
        self.assertEqual(new_test_post, first_object)

    def test_profile_view(self):
        """На странице профиля отображаются посты."""
        group_posts = PostViewsTests.group
        new_test_post = Post.objects.create(
            author=self.user,
            text='Новое тестовое сообщение',
            group=group_posts,
        )
        response = self.authorized_client.get(
            reverse(
                'posts:profile', kwargs={'username': f'{self.user.username}'}
            )
        )
        first_object = response.context['page_obj'][0]
        self.assertEqual(new_test_post, first_object)

    def test_cache(self):
        """Тестирование кэширования главной страницы"""
        def response_page():
            response = self.authorized_client.get(
                reverse('posts:index')).content.decode('UTF-8')
            return response
        cache.clear()
        text_cache = self.post.text
        self.assertIn(text_cache, response_page())
        Post.objects.filter(text=text_cache).delete()
        self.assertIn(text_cache, response_page())
        cache.clear()
        self.assertNotIn(text_cache, response_page())

    def test_follow_user(self):
        '''Проверка возможности подписаться и отписаться'''
        follower_count = Follow.objects.count()
        Follow.objects.create(
            user=self.user, author=self.user
        )
        self.assertEqual(follower_count + 1, Follow.objects.count())
        Follow.objects.filter(
            user=self.user, author=self.user).delete()
        self.assertEqual(follower_count, Follow.objects.count())

    def test_new_post_for_follower_true(self):
        '''Проверка наличия нового поста у подписчиков'''
        Follow.objects.create(
            user=self.user, author=self.user
        )
        new_post = Post.objects.create(
            author=self.user,
            text='Новое тестовое сообщение',
            group=self.group,
        )
        response = self.authorized_client.get(
            reverse('posts:follow_index')
        )
        first_object = response.context['page_obj'][0]
        self.assertEqual(new_post, first_object)

    def test_new_post_for_follower_false(self):
        '''Проверка отсутствие поста у тех, кто не подписан на автора'''
        Follow.objects.create(
            user=self.user, author=self.user
        )
        new_post = Post.objects.create(
            author=self.user,
            text='Testtext',
            group=self.group,
        )
        Follow.objects.filter(
            user=self.user, author=self.user).delete()
        response = self.authorized_client.get(
            reverse('posts:follow_index')
        )
        first_object = response.context['page_obj']
        self.assertNotEqual(first_object, new_post)
