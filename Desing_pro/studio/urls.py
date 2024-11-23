from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView
from django.conf import settings
from django.conf.urls.static import static

app_name = 'studio'

urlpatterns = [
    path('', views.home, name='home'),  # Главная страница
    path('register/', views.register, name='register'),  # Страница регистрации
    path('login/', views.login_view, name='login'),  # Страница входа
    path('logout/', LogoutView.as_view(), name='logout'),  # Используем стандартный LogoutView
    path('captcha/', views.captcha_view, name='captcha'),
    path('create-request/', views.create_request, name='create_request'),  # Создание заявки
    path('view-requests/', views.view_requests, name='view_requests'),  # Просмотр заявок
    path('delete-request/<int:request_id>/', views.delete_request, name='delete_request'),  # Удаление заявки
    path('request/<int:pk>/', views.request_detail, name='request_detail'),  # Новый путь для отдельной заявки
    path('admin-view-requests/', views.admin_view_requests, name='admin_view_requests'),  # Новое имя пути
    path('change-status/<int:pk>/', views.change_status, name='change_status'),
    path('change-status/<int:request_id>/', views.change_request_status, name='change_request_status'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)