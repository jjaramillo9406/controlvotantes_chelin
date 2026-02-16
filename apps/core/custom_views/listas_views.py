from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.decorators.http import require_http_methods

from apps.core.custom import Estadistica
from apps.core.models import Votante


@login_required(login_url=reverse_lazy('login'))
@require_http_methods(['GET', 'POST'])
def index(request):
    selected = 0
    votantes = []
    if request.method == "POST":
        if request.POST.get('user_id') != 0:
            usuario = User.objects.filter(id=request.POST.get('user_id')).first()
            if usuario.user_config.nivel == 90:
                capturadores = User.objects.filter(user_config__orientador_id=usuario.id)
                capturadores_id = []
                for capturador in capturadores:
                    capturadores_id.append(capturador.id)

                votantes = Votante.objects.filter(usuario_id__in=capturadores_id)
            else:
                if request.user.user_config.nivel == 99:
                    votantes = Votante.objects.filter(usuario_id=request.POST.get('user_id'))[:1000]
                if request.user.user_config.nivel == 90:
                    votantes = Votante.objects.filter(usuario_id=request.POST.get('user_id'),
                                                      usuario__user_config__orientador_id=request.user.id)[:1000]
            selected = request.POST.get('user_id')
        else:
            if request.user.user_config.nivel == 99:
                votantes = Votante.objects.all()
            if request.user.user_config.nivel == 90:
                votantes = Votante.objects.filter(usuario__user_config__orientador_id=request.user.id)
    else:
        if request.user.user_config.nivel == 99:
            votantes = Votante.objects.all()[:1000]
        if request.user.user_config.nivel == 90:
            votantes = Votante.objects.filter(usuario__user_config__orientador_id=request.user.id)[:1000]
    usuarios = User.objects.order_by('first_name').all()
    return render(request, "listas/index.html", {
        'listado': votantes,
        'usuarios': usuarios,
        'selected': selected
    })