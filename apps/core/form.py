from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User

from apps.core.models import Votante, UserConfig, Municipio, Puesto, MetaUsuario


class VotanteForm(forms.ModelForm):
    class Meta:
        model = Votante
        fields = ['identificacion', 'nombres', 'apellidos', 'direccion', 'telefono', 'email', 'referido', 'puesto']
        widgets = {
            'identificacion': forms.TextInput(attrs={'class': 'form-control', 'autocomplete': 'off'}),
            'nombres': forms.TextInput(attrs={'class': 'form-control', 'autocomplete': 'off'}),
            'apellidos': forms.TextInput(attrs={'class': 'form-control', 'autocomplete': 'off'}),
            'direccion': forms.TextInput(attrs={'class': 'form-control', 'autocomplete': 'off'}),
            'telefono': forms.NumberInput(attrs={'class': 'form-control', 'autocomplete': 'off'}),
            'email': forms.TextInput(attrs={'class': 'form-control', 'autocomplete': 'off'}),
            'referido': forms.TextInput(attrs={'class': 'form-control', 'autocomplete': 'off'}),
            'puesto': forms.Select(attrs={'class': 'form-control'})
        }

    def clean_identificacion(self):
        identificacion = self.cleaned_data['identificacion']
        if not identificacion.isdigit():
            raise ValidationError("La identificacion solo puede contener numeros")
        return identificacion

    def clean_nombres(self):
        return self.cleaned_data['nombres'].upper()

    def clean_apellidos(self):
        return self.cleaned_data['apellidos'].upper()

    def clean_referido(self):
        return self.cleaned_data['referido'].upper()


class UserCreateForm(forms.Form):
    NIVELES = (
        (1, 'SOLO CONSULTAS'),
        (2, 'CAPTURADOR'),
        (3, 'VALIDADOR'),
        (99, 'ADMINISTRADOR')
    )

    identificacion = forms.CharField(max_length=10, widget=forms.TextInput(attrs={'class': 'form-control text-uppercase'}))
    nombres = forms.CharField(max_length=150,widget=forms.TextInput(attrs={'class': 'form-control text-uppercase'}))
    apellidos = forms.CharField(max_length=150, widget=forms.TextInput(attrs={'class': 'form-control text-uppercase'}))
    nivel = forms.ChoiceField(choices=NIVELES, widget=forms.Select(attrs={'class': 'form-control'}))
    email = forms.EmailField(max_length=150, widget=forms.EmailInput(attrs={'class': 'form-control text-uppercase'}))
    meta = forms.IntegerField(widget=forms.NumberInput(attrs={'class': 'form-control'}))
    puesto = forms.ModelChoiceField(queryset=Puesto.objects.all(), required=False, widget=forms.Select(attrs={'class': 'form-control'}))

    def clean_identificacion(self):
        identificacion = self.cleaned_data['identificacion']
        existe_usuario = UserConfig.objects.filter(identificacion=identificacion).exists()
        if existe_usuario:
            raise ValidationError("Ya existe un usuario con este número de identificación")
        return identificacion

    def clean_nombres(self):
        return self.cleaned_data['nombres'].upper()

    def clean_apellidos(self):
        return self.cleaned_data['apellidos'].upper()

    def clean_email(self):
        return self.cleaned_data['email'].upper()


class MetaUsuarioForm(forms.ModelForm):
    class Meta:
        model = MetaUsuario
        fields = ['puesto', 'meta']
        widgets = {
            'puesto': forms.Select(attrs={'class': 'form-control'}),
            'meta': forms.NumberInput(attrs={'class': 'form-control', 'type': 'number'})
        }

    def clean_meta(self):
        meta = self.cleaned_data['meta']
        if meta <= 0:
            raise forms.ValidationError("La meta electoral debe ser igual o superior a 0")
        return meta


class MasivoVotanteForm(forms.Form):
    archivo = forms.FileField(required=True, widget=forms.FileInput(attrs={'class': 'form-control'}))

