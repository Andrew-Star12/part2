from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from .models import Request

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    captcha = forms.CharField(max_length=8, required=True, label="Введите капчу")

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def clean_captcha(self):
        captcha_input = self.cleaned_data.get('captcha')
        captcha_text = self.request.session.get('captcha_text')

        if captcha_input.lower() != captcha_text.lower():  # Сравниваем игнорируя регистр
            raise forms.ValidationError("Неверная капча.")
        return captcha_input

class CustomAuthenticationForm(AuthenticationForm):
    captcha = forms.CharField(max_length=8, required=True, label="Введите капчу")

    class Meta:
        model = User
        fields = ['username', 'password']

    def clean_captcha(self):
        captcha_input = self.cleaned_data.get('captcha')
        captcha_text = self.request.session.get('captcha_text')

        if captcha_input.lower() != captcha_text.lower():  # Сравниваем игнорируя регистр
            raise forms.ValidationError("Неверная капча.")
        return captcha_input


class RequestForm(forms.ModelForm):
    class Meta:
        model = Request
        fields = ['title', 'description', 'category', 'photo']  # Используем поле "photo"

    def clean_photo(self):
        photo = self.cleaned_data.get('photo')
        if photo:
            # Проверяем размер изображения
            if photo.size > 2 * 1024 * 1024:  # 2 МБ
                raise forms.ValidationError("Размер изображения не должен превышать 2 МБ.")

            # Проверяем формат изображения
            if not photo.name.endswith(('jpg', 'jpeg', 'png', 'bmp')):
                raise forms.ValidationError("Недопустимый формат изображения.")

        return photo