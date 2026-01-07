
class Estadistica:
    id = 0
    identificacion = ""
    nombres = ""
    apellidos = ""
    ultimo_registro = None
    registrados = 0
    zonificados = 0
    asistieron = 0
    meta = 0
    pendientes = 0
    media = 0
    municipio = ""


class EstadisticaMunicipio:
    cod_depto = ""
    nom_depto = ""
    cod_municipio = ""
    nom_municipio = ""
    meta = 0
    registrados = 0

    def to_dict(self):
        return {
            "cod_depto": self.cod_depto,
            "nom_depto": self.nom_depto,
            "cod_municipio": self.cod_municipio,
            "nom_municipio": self.nom_municipio,
            "meta": self.meta,
            "registrados": self.registrados
        }


class VotanteSearch:
    identificacion = ""
    nombres = ""
    apellidos = ""
    direccion = ""
    departamento = ""
    municipio = ""
    telefono = ""
    email = ""
    lider = ""
    fecha_registro = None
    puesto = None
    mesa = None
    estado = ""
    mensaje = ""

    def to_dict(self):
        return {
            "identificacion": self.identificacion,
            "nombres": self.nombres,
            "apellidos": self.apellidos,
            "direccion": self.direccion,
            "departamento": self.departamento,
            "municipio": self.municipio,
            "telefono": self.telefono,
            "email": self.email,
            "lider": self.lider,
            "fecha_registro": self.fecha_registro.strftime("%d %m %Y %H %M %S"),
            "puesto": self.puesto,
            "mesa": self.mesa,
            "estado": self.estado,
            "respuesta": self.mensaje
        }


