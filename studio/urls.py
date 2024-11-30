from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token

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

    path('api/token/', obtain_auth_token, name='api-token'),
    path('categories/', views.category_list, name='category_list'),
    path('categories/<int:pk>/', views.category_detail, name='category_detail'),
    path('categories/create/', views.category_create, name='category_create'),
    path('categories/edit/<int:pk>/', views.category_edit, name='category_edit'),
    path('categories/delete/<int:pk>/', views.category_delete, name='category_delete'),
    path('mark-as-paid/<int:request_id>/', views.mark_as_paid, name='mark_as_paid'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)