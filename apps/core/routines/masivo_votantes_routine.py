import pandas as pd
from django.contrib.auth.models import User
from django.db import transaction, IntegrityError

from apps.core.models import Votante, Municipio, Puesto


def load_votantes(data):
    errors = []
    has_errors = False
    df = pd.read_excel(data)
    with transaction.atomic():
        try:
            for index, row in df.iterrows():
                municipio = None
                puesto = None
                user = None
                if len(errors) > 0:
                    raise Exception("Documento no valido")
                else:
                    if index >= 0:
                        if row[0] == "":
                            errors.append(f"{index}: Nombres del votante no validos")

                        if row[1] == "":
                            errors.append(f"{index}: Apelidos del votante no validos")

                        if row[2] == "":
                            errors.append(f"{index}: Documento del votante no valido")

                        if row[5] != "":
                            municipio = Municipio.objects.filter(nombre__icontains=row[5]).first()
                            if municipio is None:
                                errors.append(f"{index}: Municipio {row[5]} no existe")
                        else:
                            errors.append(f"{index}: Municipio no validos")

                        # if row[7] != "" and not municipio is None:
                        #     puesto = Puesto.objects.filter(nombre__icontains=row[7]).first()
                        #     if puesto is None:
                        #         errors.append(f"{index}: Puesto {row[7]} no existe")
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
                                votante = Votante()
                                votante.nombres = row[0].upper()
                                votante.apellidos = row[1].upper()
                                votante.identificacion = row[2]
                                votante.telefono = row[3]
                                votante.direccion = row[4]
                                votante.municipio_id = municipio.id
                                votante.puesto_id = None
                                #votante.puesto_id = puesto.id
                                #if row[8] != "" and str(row[8]) != "nan":
                                #    votante.mesa = row[8]
                                #else:
                                #    votante.mesa = 0
                                votante.usuario_id = user.id
                                votante.asistio = False
                                votante.referido = "N/A"
                                votante.full_clean()
                                votante.save()
        except IntegrityError as e:
            errors.append(e.args[0])
        except:
            errors.append("No se pudo procesar la solicitud")
            has_errors = True
    return errors