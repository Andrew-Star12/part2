from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from django.utils import timezone
from datetime import timedelta


class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)  # Это поле должно быть здесь!
    comment = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name


class Request(models.Model):
    STATUS_CHOICES = [
        ('new', 'Новая'),
        ('in_progress', 'Принято в работу'),
        ('completed', 'Выполнено'),
    ]

    title = models.CharField(max_length=255)
    description = models.TextField()
    category = models.ForeignKey('Category', on_delete=models.CASCADE)
    photo = models.ImageField(upload_to='request_photos/', null=True, blank=True)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='new')
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    paid = models.BooleanField(default=False)  # Поле, показывающее оплачена ли заявка
    created_at = models.DateTimeField(auto_now_add=True)

    def is_payment_due(self):
        """Проверяем, если прошло более 3 дней с момента создания заявки"""
        return self.created_at <= timezone.now() - timedelta(days=3)

    def __str__(self):
        return self.title

    def get_status_display(self):
        return dict(self.STATUS_CHOICES).get(self.status, self.status)

    def clean(self):
        # Проверка максимального размера изображения
        if self.photo and self.photo.size > 2 * 1024 * 1024:  # 2 МБ
            raise ValidationError("Размер изображения не должен превышать 2 МБ.")

        # Проверка формата изображения
        if self.photo and not self.photo.name.endswith(('jpg', 'jpeg', 'png', 'bmp')):
            raise ValidationError("Недопустимый формат изображения. Разрешенные форматы: jpg, jpeg, png, bmp.")

    def get_absolute_url(self):
        return reverse('studio:request_detail', kwargs={'pk': self.pk})


