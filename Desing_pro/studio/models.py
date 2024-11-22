from django.db import models
from django.contrib.auth.models import User
from django import forms


class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Request(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    photo = models.ImageField(upload_to='requests/', null=True, blank=True)  # Фото помещения или плана

    def __str__(self):
        return self.title

    def clean(self):
        # Проверка максимального размера изображения
        if self.photo and self.photo.size > 2 * 1024 * 1024:  # 2 МБ
            raise ValidationError("Размер изображения не должен превышать 2 МБ.")

        # Проверка формата изображения
        if self.photo and not self.photo.name.endswith(('jpg', 'jpeg', 'png', 'bmp')):
            raise ValidationError("Недопустимый формат изображения. Разрешенные форматы: jpg, jpeg, png, bmp.")