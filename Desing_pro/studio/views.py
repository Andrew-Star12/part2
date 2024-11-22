from django.shortcuts import render
from .forms import CustomUserCreationForm
from django.contrib.auth import authenticate, login
from .forms import CustomAuthenticationForm
from django.contrib.auth import logout
from django.shortcuts import redirect
import random
import string
from io import BytesIO
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import UserCreationForm
from PIL import Image, ImageDraw, ImageFont
from django.http import HttpResponse
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import RequestForm
from .models import Request
from django.shortcuts import render
from .models import Request



def home(request):
    return render(request, 'studio/home.html')

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
    characters = string.ascii_lowercase + string.ascii_uppercase + string.digits
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
        form = RequestForm(request.POST, request.FILES)  # Обрабатываем файлы
        if form.is_valid():
            # Сохраняем заявку
            form.save()
            messages.success(request, 'Заявка успешно создана!')
            return redirect('studio:view_requests')  # Перенаправление на страницу просмотра заявок
        else:
            messages.error(request, 'Пожалуйста, исправьте ошибки в форме.')
    else:
        form = RequestForm()

    return render(request, 'studio/create_request.html', {'form': form})

@login_required
def view_requests(request):
    user_requests = Request.objects.filter(user=request.user)
    return render(request, 'studio/view_requests.html', {'requests': user_requests})

@login_required
def delete_request(request, request_id):
    user_request = get_object_or_404(Request, id=request_id, user=request.user)
    user_request.delete()
    messages.success(request, 'Заявка успешно удалена!')
    return redirect('studio:view_requests')


def request_detail(request, pk):
    # Получаем заявку по ее первичному ключу (ID)
    request_detail = get_object_or_404(Request, pk=pk)

    return render(request, 'studio/request_detail.html', {'request': request_detail})

def view_requests(request):
    user_requests = Request.objects.filter(user=request.user)  # Получаем заявки текущего пользователя
    return render(request, 'studio/view_requests.html', {'requests': user_requests})