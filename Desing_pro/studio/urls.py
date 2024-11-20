from django.urls import path, include
from . import views
from django.contrib.auth.views import LogoutView

app_name = 'studio'

urlpatterns = [
    path('', views.home, name='home'),  # Главная страница
    path('register/', views.register, name='register'),  # Страница регистрации
    path('login/', views.login_view, name='login'),  # Страница входа
]