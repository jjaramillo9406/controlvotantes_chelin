import json

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.decorators.http import require_http_methods

from apps.core.custom import VotanteSearch
from apps.core.models import LogAsistenciaVotante, TipoAsistencia, Votante


@login_required(login_url=reverse_lazy('login'))
@require_http_methods(['GET'])
def index(request):
    try:
        nivel = request.user.user_config.nivel
    except Exception:
        nivel = 0
    puede_registrar = nivel in [3, 99]
    return render(request, "consultas/index.html", {'puede_registrar': puede_registrar})


@login_required(login_url=reverse_lazy('login'))
@require_http_methods(['GET', 'POST'])
def search(request):
    response = VotanteSearch()
    if 'nit' in request.GET:
        votante = Votante.objects.filter(
            identificacion=request.GET['nit']).first()
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

            if not votante.tipo_asistencia is None:
                response.tipo_asistencia_id = votante.tipo_asistencia.id
                response.tipo_asistencia_nombre = votante.tipo_asistencia.nombre
                response.estado = votante.tipo_asistencia.nombre
            elif not votante.asistio is None:
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


@login_required(login_url=reverse_lazy('login'))
@require_http_methods(['POST'])
def registrar_asistencia(request):
    try:
        body = json.loads(request.body)
        identificacion = body.get('identificacion')
        tipo_asistencia_id = body.get('tipo_asistencia_id')

        if not identificacion or not tipo_asistencia_id:
            return JsonResponse({'respuesta': 'Datos incompletos'}, status=400)

        votante = Votante.objects.filter(identificacion=identificacion).first()
        if votante is None:
            return JsonResponse({'respuesta': 'Votante no encontrado'}, status=404)

        tipo_asistencia = TipoAsistencia.objects.get(id=tipo_asistencia_id)

        ip = request.META.get('HTTP_X_FORWARDED_FOR',
                              request.META.get('REMOTE_ADDR', '0.0.0.0'))
        if ',' in ip:
            ip = ip.split(',')[0].strip()

        LogAsistenciaVotante.objects.create(
            votante=votante,
            ip=ip,
            usuario=request.user,
            tipo_asistencia=tipo_asistencia,
        )

        votante.tipo_asistencia = tipo_asistencia
        votante.asistio = tipo_asistencia_id != 3
        votante.save()

        return JsonResponse({
            'respuesta': 'OK',
            'tipo_asistencia_id': tipo_asistencia.id,
            'tipo_asistencia_nombre': tipo_asistencia.nombre,
        })

    except TipoAsistencia.DoesNotExist:
        return JsonResponse({'respuesta': 'Tipo de asistencia inválido'}, status=400)
    except Exception as e:
        return JsonResponse({'respuesta': str(e)}, status=500)
