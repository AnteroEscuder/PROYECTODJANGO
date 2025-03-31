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