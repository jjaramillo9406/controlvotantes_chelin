import json

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.decorators.http import require_http_methods

from apps.core.custom import Estadistica, EstadisticaMunicipio
from apps.core.models import Votante, Municipio, UserConfig


@login_required(login_url=reverse_lazy('login'))
@require_http_methods(['GET'])
def index(request):
    usuarios = User.objects.all()
    estadisticas = []
    registros_municipios = []

    meta_electoral = 0
    total_registrados = 0

    municipios = Municipio.objects.all()

    for municipio in municipios:
        est_mun = EstadisticaMunicipio()
        est_mun.cod_depto = municipio.depto.id
        est_mun.nom_depto = municipio.depto.nombre
        est_mun.cod_municipio = municipio.id
        est_mun.nom_municipio = municipio.nombre
        est_mun.registrados = Votante.objects.filter(municipio_id=municipio.id).count()
        if est_mun.registrados > 0: registros_municipios.append(est_mun.to_dict())

    for usuario in usuarios:
        estadistica = Estadistica()
        estadistica.identificacion = usuario.user_config.identificacion
        estadistica.municipio = usuario.user_config.municipio.nombre
        estadistica.nombres = usuario.first_name
        estadistica.apellidos = usuario.last_name
        estadistica.registrados = Votante.objects.filter(usuario_id=usuario.id).count()
        estadistica.zonificados = Votante.objects.filter(usuario_id=usuario.id, zonificado=True).count()
        estadistica.asistieron = Votante.objects.filter(usuario_id=usuario.id, asistio=True).count()
        estadistica.meta = usuario.user_config.meta
        estadistica.pendientes = estadistica.meta - estadistica.registrados
        estadistica.media = estadistica.meta / 2
        ultimo = Votante.objects.filter(usuario_id=usuario.id).order_by('-creado').first()
        if not ultimo is None:
            estadistica.ultimo_registro = ultimo.creado

        meta_electoral += estadistica.meta
        total_registrados += estadistica.registrados

        estadisticas.append(estadistica)

    return render(request, "estadisticas/index.html", {
        'estadisticas': estadisticas,
        'meta_electoral': meta_electoral,
        'total_registrados': total_registrados,
        'municipios': registros_municipios
    })


@login_required(login_url=reverse_lazy('login'))
@require_http_methods(['GET'])
def est_municipios_view(request):
    municipios = Municipio.objects.order_by('-meta', 'nombre').all()
    estadisticas = []
    for municipio in municipios:
        estadistica = EstadisticaMunicipio()
        estadistica.cod_municipio = municipio.id
        estadistica.nom_municipio = municipio.nombre
        estadistica.cod_depto = municipio.depto.id
        estadistica.nom_depto = municipio.depto.nombre
        estadistica.meta = municipio.meta
        usuarios = UserConfig.objects.filter(municipio_id=municipio.id)
        for usuario in usuarios:
            estadistica.registrados += Votante.objects.filter(usuario_id=usuario.id, municipio_id=municipio.id).count()
        if estadistica.meta > 0:
            estadisticas.append(estadistica.to_dict())
    return JsonResponse(json.dumps(estadisticas), safe=False)
