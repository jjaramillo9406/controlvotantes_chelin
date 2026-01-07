from django.db import models
from django.contrib.auth.models import User
from simple_history.models import HistoricalRecords

class Departamento(models.Model):
    id = models.CharField(max_length=2, primary_key=True)
    nombre = models.CharField(max_length=150, null=False)

    def __str__(self):
        return self.nombre

    class Meta:
        db_table = 'departamentos'


class Municipio(models.Model):
    id = models.CharField(max_length=5, primary_key=True)
    depto = models.ForeignKey(Departamento, null=False, on_delete=models.RESTRICT)
    nombre = models.CharField(max_length=150, null=False)
    meta = models.PositiveIntegerField(null=False, default=0)

    def __str__(self):
        return self.nombre

    class Meta:
        db_table = 'municipios'
        ordering = ['nombre']

class Comuna(models.Model):
    municipio = models.ForeignKey(Municipio, null=False, on_delete=models.RESTRICT)
    nombre = models.CharField(max_length=150, null=False)

    def __str__(self):
        return self.nombre

    class Meta:
        db_table = 'comunas'

class UserConfig(models.Model):
    user = models.OneToOneField(User, null=False, on_delete=models.RESTRICT, related_name='user_config')
    nivel = models.PositiveIntegerField(null=False, default=0)
    identificacion = models.CharField(max_length=10, null=False, unique=True, default='')
    meta = models.PositiveIntegerField(null=False, default=0)

    class Meta:
        db_table = 'users_config'


class Puesto(models.Model):
    nombre = models.CharField(max_length=150)
    municipio = models.ForeignKey(Municipio, null=True, on_delete=models.RESTRICT)
    comuna = models.ForeignKey(Comuna, null=False, on_delete=models.RESTRICT, default='')
    estado = models.BooleanField(null=False, default=True)

    def __str__(self):
        return f"{self.municipio.nombre}-{self.nombre}"

    class Meta:
        db_table = 'puestos'
        unique_together = ['nombre', 'comuna']
        ordering = ['municipio__nombre', 'nombre']


class Votante(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.RESTRICT)
    identificacion = models.CharField(max_length=20, null=False)
    nombres = models.CharField(max_length=100, null=False)
    apellidos = models.CharField(max_length=100, null=False)
    email = models.EmailField(max_length=254, null=True, blank=True)
    telefono = models.CharField(max_length=20, null=False, blank=True)
    direccion = models.CharField(max_length=200, null=False, blank=True)
    ip = models.GenericIPAddressField(null=True, blank=True)
    puesto = models.ForeignKey(Puesto, null=True, on_delete=models.RESTRICT)
    mesa = models.PositiveIntegerField(null=True)
    zonificado = models.BooleanField(null=False, default=False)
    asistio = models.BooleanField(null=True)
    creado = models.DateTimeField(auto_now_add=True)
    actualizado = models.DateTimeField(auto_now=True)
    referido = models.CharField(max_length=100, null=True)
    municipio = models.ForeignKey(Municipio, null=False, on_delete=models.RESTRICT, default='54001')
    logs = HistoricalRecords(table_name='log_votantes')

    def __str__(self):
        return self.nombres + ' ' + self.apellidos
    
    class Meta:
        db_table = 'votantes'
        unique_together = ('identificacion', 'usuario')


class MetaUsuario(models.Model):
    user = models.ForeignKey(User, null=False, on_delete=models.RESTRICT)
    puesto = models.ForeignKey(Puesto, null=False, on_delete=models.RESTRICT)
    meta = models.PositiveIntegerField(null=False, default=0)

    def __str__(self):
        return self.puesto

    class Meta:
        db_table = 'metas_usuarios'
