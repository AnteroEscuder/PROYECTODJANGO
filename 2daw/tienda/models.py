from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import Group
from django.utils import timezone 

def crear_grupos(sender, **kwargs):
    if not Group.objects.filter(name="Clientes").exists():
        Group.objects.create(name = 'Clientes')
    if not Group.objects.filter(name="Vendedores").exists():
        Group.objects.create(name = 'Vendedores')

# Create your models here.

class Usuario (AbstractUser):
    ADMINISTRADOR = 1
    CLIENTE = 2
    VENDEDOR = 3
    ROLES = (
        (ADMINISTRADOR, 'administrador'),
        (CLIENTE, 'cliente'),
        (VENDEDOR, 'vendedor'),
    )

    rol = models.PositiveSmallIntegerField(
        choices= ROLES,default=CLIENTE
    )
    email = models.EmailField(unique=True)

class Cliente(models.Model):
    usuario = models.OneToOneField(Usuario,
                                   on_delete= models.CASCADE)    

    def __str__(self):
        return self.usuario.username
    
class Vendedor(models.Model):
    usuario = models.OneToOneField(Usuario,
                                   on_delete= models.CASCADE)


    def __str__(self):
        return self.usuario.username
    
class Inventario(models.Model):
    tienda = models.ForeignKey('Tienda', on_delete=models.CASCADE)
    medicamento = models.ForeignKey('Medicamento', on_delete=models.CASCADE)
    cantidad = models.IntegerField()
    precio = models.IntegerField(default=0)

class Medicamento(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.CharField(max_length=250)
    precio = models.IntegerField(default=0)
    fecha_caducidad = models.DateField()
    vendedor = models.ForeignKey(Vendedor, on_delete=models.CASCADE)

    def __str__(self):
        return self.nombre

class Tienda(models.Model):
    nombre = models.CharField(max_length=100)
    direccion = models.CharField(max_length=100)
    telefono = models.CharField(max_length=20)
    vendedor = models.ForeignKey(Vendedor, on_delete=models.CASCADE)

    def __str__(self):
        return self.nombre

class CuentaBancaria(models.Model):
    MONEDAS = [
        ('EUR', 'Euro'),
        ('USD', 'Dólar'),
        ('GBP', 'Libra Esterlina'),
    ]

    cliente = models.OneToOneField(Cliente, on_delete=models.CASCADE)
    iban = models.CharField(max_length=34)
    banco = models.CharField(max_length=100)
    moneda = models.CharField(max_length=3, choices=MONEDAS)
    saldo = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f"Cuenta de {self.cliente.usuario.username} - {self.iban}"

class DatosVendedor(models.Model):
    vendedor = models.OneToOneField(Vendedor, on_delete=models.CASCADE)
    direccion = models.CharField(max_length=255)
    direccion_facturacion = models.CharField(max_length=255)

    def __str__(self):
        return f"Datos de {self.vendedor.usuario.username}"

class Pedido(models.Model):
    cliente = models.ForeignKey('Cliente', on_delete=models.CASCADE)
    fecha = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Pedido {self.id} de {self.cliente.usuario.username}"

class Compra(models.Model):
    cliente = models.ForeignKey('Cliente', on_delete=models.CASCADE)
    tienda = models.ForeignKey('Tienda', on_delete=models.CASCADE)
    medicamento = models.ForeignKey('Medicamento', on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField()
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2, default=0)


    def __str__(self):
        return f"{self.cliente.usuario.username} compró"

class LineaPedido(models.Model):
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name='lineas')
    medicamento = models.ForeignKey('Medicamento', on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.cantidad} x {self.medicamento.nombre}"

class Devolucion(models.Model):
    linea_pedido = models.ForeignKey('LineaPedido', on_delete=models.CASCADE)
    cantidad_devuelta = models.PositiveIntegerField()
    fecha_solicitud = models.DateTimeField(default=timezone.now)
    aceptado = models.BooleanField(default=False)
    fecha_aceptacion = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Devolución de {self.cantidad_devuelta}x {self.linea_pedido.medicamento.nombre}"