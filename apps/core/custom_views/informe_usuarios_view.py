from io import BytesIO

import pandas as pd
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse, StreamingHttpResponse
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.decorators.http import require_http_methods

from apps.core.models import Municipio


@login_required(login_url=reverse_lazy('login'))
def informe_usuarios_view(request):
    municipios = Municipio.objects.filter(
        depto_id='54').order_by('nombre').all()
    return render(
        request,
        'informe/informe_usuarios.html',
        {'municipios': municipios}
    )


@login_required(login_url=reverse_lazy('login'))
@require_http_methods(['GET'])
def get_usuarios_by_municipio(request, municipio_id):
    try:
        usuarios = User.objects.filter(
            metausuario__puesto__comuna__municipio_id=municipio_id
        ).distinct().order_by('date_joined')

        data = [
            {
                'nombres': u.first_name,
                'apellidos': u.last_name,
                'email': u.email,
                'fecha_creacion': u.date_joined.strftime('%d/%m/%Y %H:%M') if u.date_joined else '',
            }
            for u in usuarios
        ]
        return JsonResponse(data, safe=False)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@login_required(login_url=reverse_lazy('login'))
@require_http_methods(['GET'])
def exportar_informe_usuarios(request, municipio_id):
    try:
        usuarios = User.objects.filter(
            metausuario__puesto__comuna__municipio_id=municipio_id
        ).distinct().order_by('date_joined')

        municipio = Municipio.objects.filter(id=municipio_id).first()
        municipio_nombre = municipio.nombre if municipio else municipio_id

        data = [
            {
                'Nombres': u.first_name,
                'Apellidos': u.last_name,
                'Email': u.email,
                'Fecha de registro': u.date_joined.strftime('%d/%m/%Y %H:%M') if u.date_joined else '',
            }
            for u in usuarios
        ]

        output = BytesIO()
        df = pd.DataFrame(data, columns=['Nombres', 'Apellidos', 'Email', 'Fecha de registro'])
        writer = pd.ExcelWriter(output, engine='xlsxwriter')
        df.to_excel(writer, sheet_name='Informe Usuarios', index=False)
        writer.sheets['Informe Usuarios'].autofit()
        writer.close()
        output.seek(0)

        response = StreamingHttpResponse(
            output,
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = f'attachment; filename="informe_usuarios_{municipio_nombre}.xlsx"'
        return response
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)
