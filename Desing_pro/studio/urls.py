from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView

app_name = 'studio'

urlpatterns = [
    path('', views.home, name='home'),  # Главная страница
    path('register/', views.register, name='register'),  # Страница регистрации
    path('login/', views.login_view, name='login'),  # Страница входа
    path('logout/', LogoutView.as_view(), name='logout'),  # Используем стандартный LogoutView
    path('captcha/', views.captcha_view, name='captcha'),
]