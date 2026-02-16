import requests
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponse, JsonResponse
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
            votantes = Votante.objects.filter(usuario_id=request.POST.get('user_id'))
            selected = request.POST.get('user_id')
        else:
            votantes = Votante.objects.all()
    else:
        votantes = Votante.objects.all()
    usuarios = User.objects.order_by('first_name').all()
    return render(request, "listas/index.html", {
        'listado': votantes,
        'usuarios': usuarios,
        'selected': selected
    })


@login_required(login_url=reverse_lazy('login'))
@require_http_methods(['GET'])
def descargar_reporte(request, usuario_lista_id):
    usuario_logueado_id = request.user.id
    url = f"http://impuestosmunicipalesap.com/cheliweb/reportes/{usuario_logueado_id}/{usuario_lista_id}"
    try:
        response = requests.get(url, timeout=60)
        response.raise_for_status()
        django_response = HttpResponse(
            response.content,
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        django_response['Content-Disposition'] = f'attachment; filename="reporte_votantes_{usuario_lista_id}.xlsx"'
        return django_response
    except requests.exceptions.RequestException as e:
        return JsonResponse({'error': f'Error al descargar el reporte: {str(e)}'}, status=500)