from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.

class Usuario (AbstractUser):
    ADMINISTRADOR=1
    CLIENTE=2
    VENDEDOR=3
    ROLES =(
        (ADMINISTRADOR, 'administrador'),
        (CLIENTE, 'cliente'),
        (VENDEDOR, 'vendedor'),
    )

    rol = models.PositiveSmallIntegerField(
        choices=ROLES,default=2
    )

class Cliente(models.Model):
    usuario = models.OneToOneField(Usuario,
                                   on_delete= models.CASCADE)
    
class Vendedor(models.Model):
    usuario = models.OneToOneField(Usuario,
                                   on_delete= models.CASCADE)

