from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from django.contrib.sites.models import Site
from django.contrib import messages
from django.shortcuts import redirect
from .models import Request
from django.contrib.auth.models import User

@receiver(post_save, sender=Request)
def check_payment_status(sender, instance, created, **kwargs):
    """Проверяем статус заявки после её сохранения"""
    if created:  # Если заявка только что создана
        if instance.is_payment_due() and not instance.paid:
            # Если прошло более 3 дней и заявка не оплачена
            users_to_notify = [instance.user] + list(User.objects.filter(is_staff=True))  # Пользователь и администраторы

            for user in users_to_notify:
                # Добавляем уведомление
                messages.warning(user, f'Заявка "{instance.title}" не оплачена в течение 3 дней. '
                                       f'Пожалуйста, проверьте статус: <a href="{instance.get_absolute_url()}">Ссылка на заявку</a>.')
