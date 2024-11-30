from .forms import CustomUserCreationForm
from .forms import CustomAuthenticationForm
from django.contrib.auth import logout
import random
from io import BytesIO
from django.contrib.auth import authenticate, login
from PIL import Image, ImageDraw, ImageFont
from .forms import RequestForm
from .forms import StatusChangeForm
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .forms import RequestFilterForm
from .forms import CategoryForm
from django.utils import timezone
from datetime import timedelta
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from .models import Request
from django.http import JsonResponse, HttpResponse
from rest_framework.parsers import JSONParser
from .models import Category
from .serializers import CategorySerializer
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Category
from .serializers import CategorySerializer



def home(request):
    # Получаем все заявки, которые не оплачены более 3 дней
    unpaid_requests = Request.objects.filter(
        paid=False,
        created_at__lte=timezone.now() - timedelta(days=3)
    )

    # Передаем в контекст уведомления для пользователя и администратора
    context = {
        'unpaid_requests': unpaid_requests,
    }

    return render(request, 'studio/home.html', context)

def register(request):
    form = CustomUserCreationForm()  # Инициализируем форму до проверки POST запроса

    if request.method == 'POST':
        captcha_input = request.POST.get('captcha')  # Введённый текст капчи
        captcha_text = request.session.get('captcha_text')  # Текст капчи из сессии

        if captcha_input and captcha_input == captcha_text:
            form = CustomUserCreationForm(request.POST)  # Используем кастомную форму
            if form.is_valid():
                user = form.save()  # Создаем нового пользователя
                messages.success(request, 'Регистрация прошла успешно!')
                return redirect('studio:login')  # Перенаправляем на страницу входа
            else:
                messages.error(request, 'Форма заполнена неверно.')
        else:
            messages.error(request, 'Неверная капча.')

    return render(request, 'registration/register.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('studio:home')
            else:
                form.add_error(None, 'Неверные учетные данные')
        else:
            # Ошибка валидации формы, например, капча не совпала
            pass
    else:
        form = CustomAuthenticationForm()

    return render(request, 'registration/login.html', {'form': form})
def logout_view(request):
    logout(request)
    return redirect('studio:home')  # перенаправление на главную страницу после выхода

def generate_captcha_text(length=5):
    characters = "абвгдеёжзийклмнопрстуфхцчшщьыэюя"  # Кириллические буквы
    characters += characters.upper()  # Добавляем заглавные кириллические буквы
    characters += "0123456789"  # Добавляем цифры
    return ''.join(random.choice(characters) for _ in range(length))

def create_captcha_image(captcha_text):
    width, height = 200, 60
    image = Image.new('RGB', (width, height), color=(255, 255, 255))
    draw = ImageDraw.Draw(image)

    # Используем стандартный шрифт, если не можем найти другой
    try:
        font = ImageFont.truetype("arial.ttf", 40)
    except IOError:
        font = ImageFont.load_default()

    # Рисуем текст капчи
    draw.text((50, 10), captcha_text, font=font, fill=(0, 0, 0))

    img_io = BytesIO()
    image.save(img_io, 'PNG')
    img_io.seek(0)
    return img_io


def captcha_view(request):
    # Генерируем капчу
    captcha_text = generate_captcha_text()

    # Сохраняем капчу в сессии, чтобы сравнивать при отправке формы
    request.session['captcha_text'] = captcha_text

    # Создаем изображение капчи
    img_io = create_captcha_image(captcha_text)

    # Отправляем изображение капчи в ответ
    return HttpResponse(img_io, content_type='image/png')

@login_required
def create_request(request):
    if request.method == 'POST':
        form = RequestForm(request.POST, request.FILES)
        if form.is_valid():
            request_instance = form.save(commit=False)
            request_instance.user = request.user
            request_instance.save()

            messages.success(request, 'Заявка успешно создана!')
            return redirect('studio:view_requests')
    else:
        form = RequestForm()

    return render(request, 'studio/create_request.html', {'form': form})

@login_required
def view_requests(request):
    # Получаем все заявки пользователя
    user_requests = Request.objects.filter(user=request.user)

    # Фильтрация по статусу
    form = RequestFilterForm(request.GET)  # Используем GET для получения данных формы
    if form.is_valid():
        status = form.cleaned_data.get('status')
        if status:
            user_requests = user_requests.filter(status=status)

    return render(request, 'studio/view_requests.html', {
        'requests': user_requests,
        'form': form,
    })

@login_required
def delete_request(request, request_id):
    user_request = get_object_or_404(Request, id=request_id, user=request.user)
    user_request.delete()
    messages.success(request, 'Заявка успешно удалена!')
    return redirect('studio:view_requests')


@login_required
def request_detail(request, pk):
    # Получаем заявку по ее первичному ключу (ID)
    user_request = get_object_or_404(Request, pk=pk)

    # Проверяем, является ли пользователь администратором или владельцем заявки
    if not request.user.is_staff and request.user != user_request.user:
        messages.error(request, 'У вас нет прав для изменения этой заявки.')
        return redirect('studio:view_requests')

    # Обработка формы для изменения статуса
    if request.method == 'POST':
        form = StatusChangeForm(request.POST, instance=user_request)
        if form.is_valid():
            form.save()  # Сохраняем новый статус
            messages.success(request, f"Статус заявки '{user_request.title}' изменен!")
            return redirect('studio:request_detail', pk=user_request.pk)  # Оставляем на этой же странице
    else:
        form = StatusChangeForm(instance=user_request)

    return render(request, 'studio/request_detail.html', {
        'request': user_request,
        'form': form
    })

@login_required
def change_status(request, pk):
    # Получаем заявку по ее первичному ключу
    request_instance = get_object_or_404(Request, pk=pk)

    # Проверяем, является ли пользователь владельцем заявки
    if request.user != request_instance.user:
        messages.error(request, 'У вас нет прав для изменения статуса этой заявки.')
        return redirect('studio:view_requests')

    if request.method == 'POST':
        form = StatusChangeForm(request.POST, instance=request_instance)
        if form.is_valid():
            form.save()
            messages.success(request, 'Статус заявки изменен!')
            return redirect('studio:request_detail', pk=request_instance.pk)
    else:
        form = StatusChangeForm(instance=request_instance)

    return render(request, 'studio/change_status.html', {'form': form, 'request': request_instance})

@staff_member_required  # Убедимся, что доступ имеют только администраторы
def admin_view_requests(request):
    # Получаем все заявки
    requests = Request.objects.all()

    return render(request, 'studio/admin_view_requests.html', {'requests': requests})


@staff_member_required  # Убедимся, что доступ имеют только администраторы
def change_request_status(request, request_id):
    # Получаем заявку по ID
    user_request = get_object_or_404(Request, id=request_id)

    # Проверяем, что статус допустимый
    if request.method == 'POST':
        form = StatusChangeForm(request.POST, instance=user_request)
        if form.is_valid():
            form.save()  # Сохраняем новый статус
            messages.success(request, f"Статус заявки '{user_request.title}' изменен!")
            return redirect('studio:admin_view_requests')  # Возвращаем на страницу с заявками
    else:
        form = StatusChangeForm(instance=user_request)

    return render(request, 'studio/change_status.html', {'form': form, 'request': user_request})

def change_status(request, pk):
    # Получаем заявку по первичному ключу
    request_instance = get_object_or_404(Request, pk=pk)

    # Изменяем статус, например, на "Принято в работу"
    if request_instance.status == 'new':
        request_instance.status = 'in_progress'
    elif request_instance.status == 'in_progress':
        request_instance.status = 'completed'
    else:
        # Уже завершено, ничего не делаем
        pass

    request_instance.save()

    # Перенаправляем на страницу всех заявок
    return redirect('studio:view_requests')


@staff_member_required
def category_list(request):
    categories = Category.objects.all()
    return render(request, 'studio/category_list.html', {'categories': categories})

@staff_member_required
def category_create(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('studio:category_list')
    else:
        form = CategoryForm()
    return render(request, 'studio/category_form.html', {'form': form})

@staff_member_required
def category_edit(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            return redirect('studio:category_list')
    else:
        form = CategoryForm(instance=category)
    return render(request, 'studio/category_form.html', {'form': form})

@staff_member_required
def category_delete(request, pk):
    category = get_object_or_404(Category, pk=pk)
    category.delete()
    return redirect('studio:category_list')


@staff_member_required  # Убедимся, что доступ только для менеджеров
def mark_as_paid(request, request_id):
    user_request = get_object_or_404(Request, id=request_id)

    # Помечаем заявку как оплаченную
    if not user_request.paid:
        user_request.paid = True
        user_request.save()
        messages.success(request, f"Заявка '{user_request.title}' успешно помечена как оплаченная.")
    else:
        messages.info(request, f"Заявка '{user_request.title}' уже оплачена.")

    return redirect('studio:admin_view_requests')  # Перенаправляем обратно на список заявок





@csrf_exempt
def category_list(request):
    """
    List all categories, or create a new category.
    """
    if request.method == 'GET':
        categories = Category.objects.all()
        serializer = CategorySerializer(categories, many=True)
        return JsonResponse(serializer.data, safe=False)

    elif request.method == 'POST':
        data = JSONParser().parse(request)
        serializer = CategorySerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data, status=201)
        return JsonResponse(serializer.errors, status=400)


@csrf_exempt
def category_detail(request, pk):
    """
    Retrieve, update or delete a category.
    """
    try:
        category = Category.objects.get(pk=pk)
    except Category.DoesNotExist:
        return HttpResponse(status=404)

    if request.method == 'GET':
        serializer = CategorySerializer(category)
        return JsonResponse(serializer.data)

    elif request.method == 'PUT':
        data = JSONParser().parse(request)
        serializer = CategorySerializer(category, data=data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data)
        return JsonResponse(serializer.errors, status=400)

    elif request.method == 'DELETE':
        category.delete()
        return HttpResponse(status=204)



@api_view(['GET', 'POST'])
def category_list(request):
    """
    List all categories, or create a new category.
    """
    if request.method == 'GET':
        categories = Category.objects.all()
        serializer = CategorySerializer(categories, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = CategorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'DELETE'])
def category_detail(request, pk):
    """
    Retrieve, update, or delete a category.
    """
    try:
        category = Category.objects.get(pk=pk)
    except Category.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = CategorySerializer(category)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = CategorySerializer(category, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        category.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)