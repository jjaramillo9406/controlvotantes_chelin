from django.core.exceptions import PermissionDenied
from django.http import StreamingHttpResponse
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, authenticate
from django.urls import reverse_lazy
from django.views.decorators.http import require_http_methods

from apps.core.http import get_user_ip

from apps.core.form import VotanteForm
from apps.core.models import Votante, UserConfig, Puesto
from apps.core.reports import generate_excel_lista


def sign_in(request):
    if request.user.is_authenticated:
        return redirect('index')
    else:
        if request.method == 'POST':
            username = request.POST.get('username')
            password = request.POST.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                if user.is_active:
                    config = UserConfig.objects.filter(user_id=user.id).first()
                    if not config is None:
                        request.session["nivel"] = config.nivel
                        login(request, user)
                        return redirect('index')
                    else:
                        messages.error(request, "Configuración de usuario no valida")
                else:
                    messages.error(request, 'Su usuario se encuentra inactivo')
            else:
                messages.error(request, 'Nombre de usuario y/o contraseña incorrectos')

        return render(request, 'login.html')


@login_required(login_url=reverse_lazy('login'))
def sign_out(request):
    logout(request)
    return redirect('login')

@login_required(login_url=reverse_lazy('login'))
def index(request):
    votantes = Votante.objects.filter(usuario_id=request.user.id)
    form = VotanteForm()
    return render(request, 'index.html', {
        'listado': votantes,
        'form': form
    })

@login_required(login_url=reverse_lazy('login'))
def exportar_votantes(request):
    votantes = Votante.objects.filter(usuario_id=request.user.id)
    reporte = generate_excel_lista(votantes)
    response = StreamingHttpResponse(reporte,
                                        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename=reporte.xlsx'
    return response


@login_required(login_url=reverse_lazy('login'))
def registrar_votante(request):
    form = VotanteForm()
    if request.method == "POST":
        form = VotanteForm(request.POST)
        if form.is_valid():
            existe = Votante.objects.filter(identificacion=form.cleaned_data['identificacion'])
            if not existe:
                votante = form.save(commit=False)
                puesto = Puesto.objects.filter(id=votante.puesto_id).first()
                votante.usuario_id = request.user.id
                votante.nombres = votante.nombres.upper()
                votante.apellidos = votante.apellidos.upper()
                votante.municipio_id = puesto.municipio_id
                if not votante.email is None:
                    votante.email = votante.email.upper()
                if not votante.direccion is None:
                    votante.direccion = votante.direccion.upper()
                votante.ip = get_user_ip(request)
                votante.save()
                messages.success(request, "Datos guardados correctamente")
                return redirect('index')
            else:
                messages.error(request, "Ya existe el registro de este votante")
    return render(request, 'registrar_votante.html', {
        'form': form
    })


@login_required(login_url=reverse_lazy('login'))
@require_http_methods(['GET', 'POST'])
def editar_votante(request, pk):
    votante = Votante.objects.filter(pk=pk).first()
    if not votante is None:
        if votante.usuario_id == request.user.id:
            form = VotanteForm(instance=votante)
            if request.method == 'POST':
                form = VotanteForm(request.POST, instance=votante)
                if form.is_valid():
                    form.save()
                    messages.success(request, "Datos actualizados correctamente")
                    return redirect('index')
            return render(request, "editar_votante.html", {
                'form': form
            })
        else:
            raise PermissionDenied
    else:
        messages.error(request, "Votante no existe")
        return redirect('index')
