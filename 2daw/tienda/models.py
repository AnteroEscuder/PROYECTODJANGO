from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import Group

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
    

class Medicamento(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.CharField(max_length=250)
    precio = models.IntegerField(default=0)
    fecha_caducidad = models.DateField()

    def __str__(self):
        return self.nombre

class Tienda(models.Model):
    nombre = models.CharField(max_length=100)
    direccion = models.CharField(max_length=100)
    telefono = models.CharField(max_length=20)

    def __str__(self):
        return self.nombre
