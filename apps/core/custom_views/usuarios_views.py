from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from django.shortcuts import render, redirect
from django.urls import reverse_lazy

from apps.core.form import UserCreateForm
from apps.core.models import UserConfig


@login_required(login_url=reverse_lazy('login'))
def index(request):
    if request.user.user_config.nivel == 99:
        usuarios = User.objects.all()
        return render(request, "usuarios/index.html", {
            'usuarios': usuarios
        })
    else:
        raise PermissionDenied


@login_required(login_url=reverse_lazy('login'))
def create(request):
    form = UserCreateForm()
    if request.method == "POST":
        form = UserCreateForm(request.POST)
        if form.is_valid():
            user = User()
            user.first_name = form.cleaned_data['nombres']
            user.last_name = form.cleaned_data['apellidos']
            user.email = form.cleaned_data['email']
            user.set_password(form.cleaned_data['identificacion'])
            user.is_active = True
            user.username = form.cleaned_data['email'].lower()
            user.save()
            user_config = UserConfig()
            user_config.user_id = user.id
            user_config.identificacion = form.cleaned_data['identificacion']
            user_config.nivel = form.cleaned_data['nivel']
            user_config.meta = form.cleaned_data['meta']
            user_config.municipio_id = form.cleaned_data['municipio'].id
            user_config.save()
            messages.success(request, "Usuario creado exitosamente")
            return redirect('usuarios')
    return render(request, "usuarios/create.html", {
        'form': form
    })
