from django.db import models

# Create your models here.
class Cliente(models.Model):
    nombre= models.CharField(max_length=100)
    apellidos= models.CharField(max_length=100)
    usuarios= models.CharField(max_length=100)