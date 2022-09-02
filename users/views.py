import logging

from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.contrib import messages

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm

logger = logging.getLogger(__name__)


def login_page(request):
    if request.user.is_authenticated:
        return redirect(reverse_lazy('vacations:index'))

    form = AuthenticationForm()

    if request.method == 'POST':
        if request.user.is_authenticated:
            return redirect(reverse_lazy('vacations:index'))

        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            logger.debug(f'Successfully logged in: username={username}, password={password}')
            return redirect('vacations:index')
        else:
            logger.debug(f'Not logged in: username={username}, password={password}')
            messages.info(request, 'Неверный логин или пароль!')

        form = AuthenticationForm(request.POST)
        if form.is_valid():
            form.save()
            #user = form.cleaned_data.get('username')
            #messages.success(request, 'Выполнен вход пользователя ' + user)
            return redirect('login')

    context = {'form': form}
    return render(request, 'auth/login.html', context)


def logout_view(request):
    logout(request)
    return redirect(reverse_lazy('accounts:login'))

