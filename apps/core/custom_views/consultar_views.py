import json

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.decorators.http import require_http_methods

from apps.core.custom import VotanteSearch
from apps.core.models import Votante


@login_required(login_url=reverse_lazy('login'))
@require_http_methods(['GET'])
def index(request):
    return render(request, "consultas/index.html")


@login_required(login_url=reverse_lazy('login'))
@require_http_methods(['GET','POST'])
def search(request):
    response = VotanteSearch()
    if 'nit' in request.GET:
        votante = Votante.objects.filter(identificacion=request.GET['nit']).first()
        if not votante is None:
            response.identificacion = votante.identificacion
            response.nombres = votante.nombres
            response.apellidos = votante.apellidos
            response.direccion = votante.direccion
            response.departamento = votante.municipio.depto.nombre
            response.municipio = votante.municipio.nombre
            response.telefono = votante.telefono
            response.email = votante.email
            response.lider = votante.usuario.first_name + " " + votante.usuario.last_name
            response.fecha_registro = votante.creado
            if not votante.puesto_id is None:
                response.puesto = votante.puesto.nombre
                response.mesa = votante.mesa
            response.mensaje = "OK"

            if votante.zonificado:
                response.estado = "Zonificado"

            if not votante.asistio is None:
                if votante.asistio:
                    response.estado = "Asistió al puesto de votación"
                else:
                    response.estado = "No asistió al puesto de votación"
            else:
                if response.estado == "":
                    response.estado = "Registrado"

        else:
            response.mensaje = "No existen registros con este documento"
    else:
        response.mensaje = "Debe ingresar un documento"
    return JsonResponse(json.dumps(response.to_dict()), safe=False)

