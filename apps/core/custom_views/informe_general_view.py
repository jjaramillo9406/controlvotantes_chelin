from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from django.db.models import Count
from apps.core.models import Municipio, Votante


@login_required(login_url=reverse_lazy('login'))
def informe_general_view(request):
    municipios = Municipio.objects.filter(
        depto=54).order_by('nombre')

    return render(request, 'informe/informe_general.html', {
        'municipios': municipios
    })


@login_required(login_url=reverse_lazy('login'))
@require_http_methods(['GET'])
def get_puestos_by_municipio(request, municipio_id):
    try:
        puestos_data = Votante.objects.filter(
            municipio_id=municipio_id,
            puesto__isnull=False,
            mesa__isnull=False
        ).values(
            'puesto__id',
            'puesto__nombre',
            'mesa'
        ).annotate(
            total_votantes=Count('id')
        ).order_by('puesto__nombre', 'mesa')

        puestos_agrupados = {}
        for item in puestos_data:
            puesto_id = item['puesto__id']
            puesto_nombre = item['puesto__nombre']

            if puesto_id not in puestos_agrupados:
                puestos_agrupados[puesto_id] = {
                    'id': puesto_id,
                    'nombre': puesto_nombre,
                    'total_votantes': 0,
                    'mesas': []
                }

            puestos_agrupados[puesto_id]['total_votantes'] += item['total_votantes']
            puestos_agrupados[puesto_id]['mesas'].append({
                'numero': item['mesa'],
                'total_votantes': item['total_votantes']
            })

        puestos_list = list(puestos_agrupados.values())
        return JsonResponse(puestos_list, safe=False)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@login_required(login_url=reverse_lazy('login'))
@require_http_methods(['GET'])
def get_votantes_by_puesto_and_mesa(request, puesto_id, mesa):
    try:
        votantes = Votante.objects.filter(
            puesto_id=puesto_id,
            mesa=mesa
        ).select_related('usuario').order_by('usuario__first_name', 'usuario__last_name', 'apellidos', 'nombres')

        votantes_data = []
        for v in votantes:
            lider_nombre = 'Sin líder'
            if v.usuario:
                lider_nombre = f"{v.usuario.first_name} {v.usuario.last_name}".strip(
                )
                if not lider_nombre:
                    lider_nombre = v.usuario.username

            votantes_data.append({
                'id': v.id,
                'identificacion': v.identificacion,
                'nombres': v.nombres,
                'apellidos': v.apellidos,
                'lider': lider_nombre,
                'zonificado': v.zonificado,
                'asistio': v.asistio
            })

        return JsonResponse({
            'votantes': votantes_data,
            'total': len(votantes_data)
        }, safe=False)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)
