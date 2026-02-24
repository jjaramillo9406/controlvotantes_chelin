import math

import pandas as pd
from django.contrib.auth.models import User
from django.db import transaction, IntegrityError

from apps.core.models import Votante, Municipio, Puesto


def load_votantes(data):
    errors = []
    has_errors = False
    df = pd.read_excel(data)
    with transaction.atomic():
        for index, row in df.iterrows():
            municipio = None
            puesto = None
            user = None
            if len(errors) > 0:
                raise Exception(errors[0])
            else:
                if index >= 0:
                    row[2] = str(row[2]).replace(" ", "")
                    if row[2] != 'nan':
                        if row[0] == "":
                            errors.append(f"{index}: Nombres del votante no validos")

                        if row[2] == "":
                            errors.append(f"{index}: Documento del votante no valido")

                        if row[5] != "":
                            municipio = Municipio.objects.filter(nombre__icontains=row[5].strip()).first()
                            if municipio is None:
                                errors.append(f"{index}: Municipio {row[5]} no existe")
                        else:
                            errors.append(f"{index}: Municipio no validos")

                        if row[7] != "" and not municipio is None:
                            if row[7].startswith("-"):
                                row[7] = row[7].replace("-", "")
                                row[7] = row[7].strip()
                            puesto = Puesto.objects.filter(nombre__icontains=row[7].strip()).first()
                            if puesto is None:
                                errors.append(f"{index}: Puesto {row[7]} no existe")
                        # else:
                        #     errors.append(f"{index}: Puesto no validos")

                        if row[9] != "":
                            user = User.objects.filter(email__iexact=row[9].strip()).first()
                            if user is None:
                                errors.append(f"{index}: Usuario no existe")
                        else:
                            errors.append(f"{index}: Usuario no valido")

                        if len(errors) == 0:
                            if not Votante.objects.filter(identificacion=row[2]).exists():
                                if row[1] is None or str(row[1]) == "nan":
                                    row[1] = ""
                                votante = Votante()
                                votante.nombres = row[0].upper()
                                votante.apellidos = row[1].upper()
                                votante.identificacion = row[2]
                                votante.telefono = row[3]
                                votante.direccion = row[4]
                                votante.municipio_id = municipio.id
                                votante.puesto_id = None
                                votante.puesto = None
                                votante.mesa = 0
                                votante.puesto_id = puesto.id
                                if row[8] != "" and str(row[8]) != "nan":
                                    votante.mesa = row[8]
                                else:
                                    votante.mesa = 0
                                votante.usuario_id = user.id
                                votante.asistio = False
                                votante.referido = "N/A"

                                if votante.apellidos == "":
                                    datos_nombre = votante.nombres.split(" ")
                                    if len(datos_nombre) == 2:
                                        votante.nombres = datos_nombre[0]
                                        votante.apellidos = datos_nombre[1]
                                    if len(datos_nombre) == 3:
                                        votante.nombres = datos_nombre[0]
                                        votante.apellidos = f"{datos_nombre[1]} {datos_nombre[2]}"
                                    if len(datos_nombre) == 4:
                                        votante.nombres = f"{datos_nombre[0]} {datos_nombre[1]}"
                                        votante.apellidos = f"{datos_nombre[2]} {datos_nombre[3]}"
                                    if len(datos_nombre) == 5:
                                        votante.nombres = f"{datos_nombre[0]} {datos_nombre[1]}"
                                        votante.apellidos = f"{datos_nombre[2]} {datos_nombre[3]} {datos_nombre[4]}"
                                    if len(datos_nombre) == 6:
                                        votante.nombres = f"{datos_nombre[0]} {datos_nombre[1]}"
                                        votante.apellidos = f"{datos_nombre[2]} {datos_nombre[3]} {datos_nombre[4]} {datos_nombre[5]}"

                                votante.full_clean()
                                votante.save()
    return errors