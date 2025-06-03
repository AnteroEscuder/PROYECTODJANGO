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
        fields = ['nombre','descripcion','precio','fecha_caducidad']
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
        fields = ['nombre','direccion','telefono']
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

    def clean(self):
        cleaned_data = super().clean()
        iban = cleaned_data.get('iban')
        banco = cleaned_data.get('banco')

        if iban:
            import re
            if not re.match(r'^[A-Z]{2}\d{2}[A-Z0-9]{10,30}$', iban):
                self.add_error('iban', 'IBAN inválido. Debe comenzar con 2 letras, 2 números y contener entre 10 y 30 caracteres alfanuméricos adicionales.')

        if banco and len(banco.strip()) < 3:
            self.add_error('banco', 'El nombre del banco debe tener al menos 3 caracteres.')

        return cleaned_data

class DatosVendedorForm(forms.ModelForm):
    class Meta:
        model = DatosVendedor
        fields = ['direccion', 'direccion_facturacion']
        widgets = {
            'direccion': forms.TextInput(attrs={'class': 'form-control'}),
            'direccion_facturacion': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        direccion = cleaned_data.get('direccion')
        direccion_facturacion = cleaned_data.get('direccion_facturacion')

        if direccion and len(direccion.strip()) < 10:
            self.add_error('direccion', 'La dirección debe tener al menos 10 caracteres.')

        if direccion_facturacion and len(direccion_facturacion.strip()) < 10:
            self.add_error('direccion_facturacion', 'La dirección de facturación debe tener al menos 10 caracteres.')

        return cleaned_data
        
class InventarioModelForm(forms.ModelForm):
    class Meta:
        model = Inventario
        fields = ['tienda', 'medicamento', 'cantidad','precio']
        help_texts = {
            'tienda': 'Selecciona la tienda',
            'medicamento': 'Selecciona el medicamento',
            'cantidad': 'Cantidad disponible en tienda',
            'precio': 'Precio del producto'
        }

    def clean(self):
        cleaned_data = super().clean()
        precio = cleaned_data.get('precio')

        if precio <= 0:
            self.add_error('precio', 'El precio tiene que ser positivo')

        return cleaned_data

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request", None)
        super(InventarioModelForm, self).__init__(*args, **kwargs)

        if self.request:
            tiendasdisponibles = Tienda.objects.filter(vendedor_id=self.request.user.vendedor).all()
            self.fields['tienda'] = forms.ModelChoiceField(
                queryset=tiendasdisponibles,
                widget=forms.Select,
                required=True,
                empty_label="Ninguna"
            )

class PedidoForm(forms.ModelForm):
    class Meta:
        model = Pedido
        fields = ['cliente']


class CompraForm(forms.Form):
    tienda = forms.ModelChoiceField(queryset=Tienda.objects.none(), label="Selecciona tienda")
    cantidad = forms.IntegerField(min_value=1, label="Cantidad")

    def __init__(self, medicamento, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if medicamento is not None:
            self.medicamento = medicamento
            tiendas_con_stock = Inventario.objects.filter(medicamento=medicamento, cantidad__gt=0)
            self.fields['tienda'].queryset = Tienda.objects.filter(id__in=tiendas_con_stock.values_list("tienda_id", flat=True))

    def clean(self):
        cleaned_data = super().clean()
        tienda = cleaned_data.get('tienda')
        cantidad = cleaned_data.get('cantidad')

        if tienda and cantidad:
            inventario = Inventario.objects.filter(tienda=tienda, medicamento=self.medicamento).first()
            if not inventario:
                self.add_error('tienda', "No hay stock disponible.")
            elif cantidad > inventario.cantidad:
                self.add_error('cantidad', f"Solo hay {inventario.cantidad} unidades en stock.")

class AñadirAlCarritoForm(forms.Form):
    cantidad = forms.IntegerField(min_value=1, label="Unidades")