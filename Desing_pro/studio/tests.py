from django.test import TestCase
from .models import Request, Category
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta


class RequestNotificationTest(TestCase):

    def setUp(self):
        # Создайте категорию для заявки
        self.category = Category.objects.create(name="Тестовая категория")

        # Создайте пользователя
        self.user = User.objects.create_user(username="testuser", password="testpassword")

        # Создайте заявку, указав категорию и пользователя
        # Установите дату создания на 4 дня назад, вручную
        self.created_at = timezone.now() - timedelta(days=4)
        self.request = Request.objects.create(
            title="Тестовая заявка",
            description="Описание заявки",
            category=self.category,
            user=self.user,
            paid=False,  # Заявка не оплачена
        )

        # Принудительно установим дату создания
        self.request.created_at = self.created_at
        self.request.save()

    def test_notification_for_unpaid_request(self):
        # Логика теста: проверка, что уведомление создается для заявки, которая не оплачена больше 3 дней
        request = self.request

        # Проверяем, что уведомление о неуплаченной заявке есть
        self.assertTrue(request.is_payment_due())  # Теперь должно быть True

        # Дополнительно можно проверить, что уведомления отображаются на главной странице, если это необходимо
        response = self.client.get('/')
        self.assertContains(response, f'Заявка "{request.title}" не оплачена')