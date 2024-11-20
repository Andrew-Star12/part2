
from django.shortcuts import render, redirect
from django.shortcuts import render, redirect
from django.contrib.auth import login
from .forms import CustomUserCreationForm, CustomAuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from .forms import CustomAuthenticationForm



def home(request):
    return render(request, 'studio/home.html')

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()  # Создаем нового пользователя
            login(request, user)  # Выполняем вход
            return redirect('studio:home')  # Перенаправляем на главную страницу
    else:
        form = CustomUserCreationForm()

    return render(request, 'registration/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()  # Получаем пользователя из формы
            login(request, user)  # Выполняем вход
            return redirect('studio:home')  # Перенаправляем на главную страницу
    else:
        form = CustomAuthenticationForm()

    return render(request, 'registration/login.html', {'form': form})