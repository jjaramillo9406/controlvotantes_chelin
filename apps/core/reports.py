from io import BytesIO
import pandas as pd

def generate_excel_lista(votantes):
    data = [
        {
            'Identificacion': item.identificacion,
            'Nombres': item.nombres,
            'Apellidos': item.apellidos,
            'Direccion': item.direccion,
            'Departamento': item.municipio.depto.nombre,
            'Municipio': item.municipio.nombre,
            'Telefono': item.telefono,
            'Puesto': item.puesto.nombre if not item.puesto is None else "N/A",
            'Mesa': item.mesa if not item.mesa is None else "N/A",
            'FechaRegistro': str(item.creado),
            'Capturador': item.usuario.first_name + " " + item.usuario.last_name
        }
        for item in votantes
    ]

    output = BytesIO()

    df = pd.DataFrame(data, columns=['Identificacion', 'Nombres', 'Apellidos', 'Direccion', 'Departamento', 'Municipio', 'Telefono', 'Puesto', 'Mesa', 'FechaRegistro', 'Capturador'])
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    df.to_excel(writer, sheet_name='Reporte')
    writer.sheets['Reporte'].autofit()
    writer.close()
    output.seek(0)
    return output