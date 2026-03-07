from django.db import connection

from apps.administracion.custom.informe_lider import InformeLider
from apps.administracion.custom.informe_puesto import InformePuesto


def get_informe_lideres(us_id):
    with connection.cursor() as cursor:
        cursor.execute(f"select (get_informe_lideres_fn({us_id})).*")
        rows = cursor.fetchall()

        informes = []
        for row in rows:
            informe = InformeLider(
                lider=row[0],
                votantes=row[1],
                pendientes=row[2],
                asis_pres=row[3],
                asis_no_pres=row[4],
                no_asis=row[5]
            )
            informes.append(informe)

        return informes

def get_informe_puestos(us_id):
    with connection.cursor() as cursor:
        cursor.execute(f"select (get_informe_puestos_fn({us_id})).*")
        rows = cursor.fetchall()

        informes = []
        for row in rows:
            informe = InformePuesto(
                depto=row[0],
                muni=row[1],
                puesto=row[2],
                mesa=row[3],
                votantes=row[4],
                pendientes=row[5],
                asis_pres=row[6],
                asis_no_pres=row[7],
                no_asis=row[8]
            )
            informes.append(informe)

        return informes
