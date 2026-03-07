import json
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.http import JsonResponse
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.decorators.http import require_http_methods
from apps.core.models import Votante, Puesto
from apps.administracion import sql
from apps.administracion.custom import informe_lider

@login_required(login_url=reverse_lazy('login'))
def verificar_votantes_view(request):
    return render(request, "administracion/verificar.html", {})

@login_required(login_url=reverse_lazy('login'))
@require_http_methods(['GET'])
def get_votantes_pendientes(request):
    votantes = Votante.objects.filter(puesto_id=None)[:100]
    votantes_response = [
        {
            'id': item.id,
            'identificacion': item.identificacion,
            'nombres': item.nombres,
            'apellidos': item.apellidos,
            'telefono': item.telefono,
            'email': item.email,
            'lider': item.usuario.first_name + " " + item.usuario.last_name
        }
        for item in votantes
    ]
    return JsonResponse(votantes_response, safe=False)


@login_required(login_url=reverse_lazy('login'))
@require_http_methods(['GET'])
def get_puestos_votacion(request):
    puestos = Puesto.objects.all().order_by('comuna__municipio__depto_id', 'comuna__municipio__nombre','nombre')
    puestos_response = [
        {
            'id': item.id,
            'nombre': item.nombre,
            'departamento': item.comuna.municipio.depto.nombre,
            'municipio': item.comuna.municipio.nombre
        }
        for item in puestos
    ]
    return JsonResponse(puestos_response, safe=False)


@login_required(login_url=reverse_lazy('login'))
@require_http_methods(['POST'])
def save_puesto_votante(request):
    response = ''
    try:
        if not request.body is None:
            data = json.loads(request.body)
            puesto = Puesto.objects.filter(id=data.get('puesto_id')).first()
            votante = Votante.objects.filter(id=data.get('votante_id')).first()
            mesa = int(data.get('mesa'))
            if not votante is None:
                if mesa > 0:
                    votante.puesto_id = puesto.id
                    votante.mesa = mesa
                    votante.zonificado = True
                    votante.save()
                    response = 'OK'
                else:
                    votante.puesto_id = None
                    votante.mesa = 0
                    votante.zonificado = True
                    votante.save()
                    response = 'OK'
            else:
                response = 'Votante no existe'
        else:
            response = 'Petición no valida'
    except:
        response = 'No se pudo procesar su solicitud'
    return JsonResponse({
        'response': response
    }, safe=False)


@login_required(login_url=reverse_lazy('login'))
def informe_lideres(request):
    if request.user.user_config.nivel > 90:
        informe = sql.get_informe_lideres()
        informe_puestos = sql.get_informe_puestos()
        total_asistio = sum(i.asistieron_presencial + i.asistieron_no_presencial for i in informe)
        total_no_asistio = sum(i.no_asistieron for i in informe)
        total_pendientes = sum(i.pendientes for i in informe)
        return render(request, 'administracion/informe/lideres.html', {
            'informe': informe,
            'informe_puestos': informe_puestos,
            'total_asistio': total_asistio,
            'total_no_asistio': total_no_asistio,
            'total_pendientes': total_pendientes,
        })
    else:
        raise PermissionDenied
    

@login_required(login_url=reverse_lazy('login'))
def informe_puestos(request):
    if request.user.user_config.nivel > 90:
        informe = sql.get_informe_puestos()
        total_asistio = sum(i.asistieron_presencial + i.asistieron_no_presencial for i in informe)
        total_no_asistio = sum(i.no_asistieron for i in informe)
        total_pendientes = sum(i.pendientes for i in informe)
        informe_json = json.dumps([{
            'departamento': i.departamento,
            'municipio': i.municipio,
            'puesto': i.puesto,
            'mesa': i.mesa,
            'votantes': i.votantes,
            'pendientes': i.pendientes,
            'asistieron_presencial': i.asistieron_presencial,
            'asistieron_no_presencial': i.asistieron_no_presencial,
            'no_asistieron': i.no_asistieron,
        } for i in informe])
        return render(request, 'administracion/informe/informe_puesto.html', {
            'informe_json': informe_json,
            'total_asistio': total_asistio,
            'total_no_asistio': total_no_asistio,
            'total_pendientes': total_pendientes,
        })
    else:
        raise PermissionDenied


@login_required(login_url=reverse_lazy('login'))
@require_http_methods(['GET'])
def get_votantes_puesto_mesa(request):
    if request.user.user_config.nivel <= 90:
        return JsonResponse({'error': 'Sin permiso'}, status=403)
    try:
        puesto_nombre = request.GET.get('puesto')
        mesa = request.GET.get('mesa')
        if not puesto_nombre or not mesa:
            return JsonResponse({'error': 'Parámetros requeridos'}, status=400)

        votantes = Votante.objects.filter(
            puesto__nombre=puesto_nombre, mesa=int(mesa)
        ).select_related('usuario', 'tipo_asistencia').order_by('apellidos', 'nombres')

        data = []
        for v in votantes:
            lider = f"{v.usuario.first_name} {v.usuario.last_name}".strip() if v.usuario else 'Sin líder'
            if v.tipo_asistencia_id in [1, 2]:
                estado = 'asistio'
            elif v.tipo_asistencia_id == 3:
                estado = 'no_asistio'
            else:
                estado = 'pendiente'
            data.append({
                'identificacion': v.identificacion,
                'nombres': v.nombres,
                'apellidos': v.apellidos,
                'lider': lider,
                'estado': estado,
            })

        return JsonResponse({'votantes': data, 'total': len(data)})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)