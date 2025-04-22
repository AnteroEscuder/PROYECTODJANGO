from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from.models import *
from django import forms
from django.forms import ModelForm
from django.utils import timezone
from datetime import timedelta

class RegistroForm(UserCreationForm):
    roles = ( 
        (Usuario.CLIENTE, 'cliente'),
        (Usuario.VENDEDOR, 'vendedor'),
     )
    
    rol = forms.ChoiceField(choices=roles, required=True)
    
    class Meta:
        model = Usuario
        fields = ('username','email','password1','password2','rol')

class LoginForm(AuthenticationForm):
    pass

class MedicamentoModelForm(ModelForm):
    class Meta:
        model = Medicamento
        fields = ['nombre','descripcion','precio','fecha_caducidad', 'vendedor']
        labels = {
            "nombre": ("Nombre del medicamento"),
            "descripcion": ("Descripción del medicamento"),
        }
        help_texts = {
            "nombre": ("100 caracteres como máximo"),
            "descripcion": ("Agrega la información del medicamento")
        }
        widgets = {
            'fecha_caducidad' : forms.DateInput(format="%Y-%m-%d", attrs={'type':'date'})
        }

    def clean(self):
        
        super().clean()

        nombre = self.cleaned_data.get('nombre')
        precio = self.cleaned_data.get('precio')
        fecha = self.cleaned_data.get('fecha_caducidad')
        descripcion = self.cleaned_data.get('descripcion')

        if nombre and len(nombre) < 4:
            self.add_error('nombre', 'Al menos debes introducir 4 caracteres')

        if descripcion and len(descripcion) < 10:
            self.add_error('descripcion', 'Al menos debes introducir 10 caracteres')

        if precio is not None and precio <= 0:
            self.add_error('precio', 'No pueden existir precios negativos')

        if fecha:
            hoy = timezone.now().date()
            min_fecha = hoy + timedelta(days=7)
            
            if fecha < min_fecha:
                self.add_error('fecha_caducidad', 'No pueden registrar medicamentos caducados o que caduquen en menos de 7 dias')

        return self.cleaned_data

class TiendaModelForm(ModelForm):
    class Meta:
        model = Tienda
        fields = ['nombre','direccion','telefono', 'vendedor']
        labels = {
            "nombre": ("Nombre de la tienda"),
            "direccion": ("Dirección de la tienda"),
        }
        help_texts = {
            "nombre": ("100 caracteres como máximo"),
        }

    def clean(self):
        
        super().clean()

        nombre = self.cleaned_data.get('nombre')
        direccion = self.cleaned_data.get('direccion')
        telefono = self.cleaned_data.get('telefono')

        if nombre and len(nombre) < 4:
            self.add_error('nombre', 'Al menos debes introducir 4 caracteres')

        if direccion and len(direccion) < 10:
            self.add_error('direccion', 'Al menos debes introducir 10 caracteres')

        if telefono:
            if not telefono.isdigit():
                self.add_error('telefono', 'El teléfono debe contener solo números')
            elif len(telefono) != 9:
                self.add_error('telefono', 'El teléfono tiene que tener exactamente 9 dígitos')


        return self.cleaned_data

class CuentaBancariaForm(forms.ModelForm):
    class Meta:
        model = CuentaBancaria
        fields = ['iban', 'banco', 'moneda']
        widgets = {
            'moneda': forms.Select(attrs={'class': 'form-select'}),
        }


class DatosVendedorForm(forms.ModelForm):
    class Meta:
        model = DatosVendedor
        fields = ['direccion', 'direccion_facturacion']
        widgets = {
            'direccion': forms.TextInput(attrs={'class': 'form-control'}),
            'direccion_facturacion': forms.TextInput(attrs={'class': 'form-control'}),
        }