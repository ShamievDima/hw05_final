from django.test import TestCase, Client
from django.urls import reverse


class StaticURLTests(TestCase):
    def setUp(self):
        # Устанавливаем данные для тестирования
        # Создаём экземпляр клиента. Он неавторизован.
        self.guest_client = Client()

    def test_about_authur(self):
        # Делаем запрос к странице об авторе и проверяем статус
        response = self.guest_client.get('/about/author/')
        # Утверждаем, что для прохождения теста код должен быть равен 200
        self.assertEqual(response.status_code, 200)

    def test_about_tech(self):
        # Делаем запрос к странице о технологиях и проверяем статус
        response = self.guest_client.get('/about/tech/')
        # Утверждаем, что для прохождения теста код должен быть равен 200
        self.assertEqual(response.status_code, 200)


class StaticViewsTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_author_page_accessible_by_name(self):
        """URL, генерируемый при помощи имени about:author, доступен."""
        response = self.guest_client.get(reverse('about:author'))
        self.assertEqual(response.status_code, 200)

    def test_tech_page_accessible_by_name(self):
        """URL, генерируемый при помощи имени about:tech, доступен."""
        response = self.guest_client.get(reverse('about:tech'))
        self.assertEqual(response.status_code, 200)

    def test_about_page_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_page_names = {
            'about/author.html': reverse('about:author'),
            'about/tech.html': reverse('about:tech'),
        }
        # Проверяем, что при обращении к name
        # вызывается соответствующий HTML-шаблон
        for template, reverse_name in templates_page_names.items():
            with self.subTest(template=template):
                response = self.guest_client.get(reverse_name)
                self.assertTemplateUsed(response, template)
