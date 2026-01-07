from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.decorators.http import require_http_methods

from apps.core.form import UserCreateForm, MetaUsuarioForm
from apps.core.models import UserConfig, MetaUsuario, Votante


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
            user_config.save()

            meta_electoral = MetaUsuario()
            meta_electoral.user_id = user.id
            meta_electoral.meta = user_config.meta
            meta_electoral.puesto_id = form.cleaned_data['puesto'].id
            meta_electoral.save()

            messages.success(request, "Usuario creado exitosamente")
            return redirect('usuarios')
    return render(request, "usuarios/create.html", {
        'form': form
    })


@login_required(login_url=reverse_lazy('login'))
@require_http_methods(["GET"])
def show(request, pk):
    usuario = User.objects.filter(id=pk).first()
    if usuario is not None:
        config = UserConfig.objects.filter(user_id=usuario.id).first()
        metas = MetaUsuario.objects.filter(user_id=usuario.id)
        return render(request, "usuarios/detail.html", {
            "usuario": usuario,
            "config": config,
            "metas": metas
        })
    else:
        messages.error(request, "Usuario no existe")
        return redirect('usuarios')

@login_required(login_url=reverse_lazy('login'))
@require_http_methods(["GET","POST"])
def create_meta(request, pk):
    form = MetaUsuarioForm()
    if request.method == 'POST':
        user_config = UserConfig.objects.filter(user_id=request.user.id).first()
        form = MetaUsuarioForm(request.POST)
        if form.is_valid():
            meta = form.save(commit=False)
            meta.user_id = request.user.id
            meta.save()

            user_config.meta += meta.meta
            user_config.save()

            messages.success(request, "Datos guardados correctamente")
            return redirect('usuario_detail', pk=pk)
        else:
            messages.warning(request, "Formulario no valido")
    return render(request, "usuarios/metas/create.html", {
        "form": form
    })

@login_required(login_url=reverse_lazy('login'))
@require_http_methods(["GET"])
def get_metas(request, pk):
    metas = MetaUsuario.objects.filter(user_id=pk)
    response = [
        {
            "departamento": item.puesto.municipio.depto.nombre,
            "municipio": item.puesto.municipio.nombre,
            "puesto": item.puesto.nombre,
            "meta": item.meta,
            "registrados": Votante.objects.filter(usuario_id=pk, puesto_id=item.puesto_id).count()
        } for item in metas
    ]

    return JsonResponse(response, safe=False)

