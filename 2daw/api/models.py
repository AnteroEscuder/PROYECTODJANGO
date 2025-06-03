from django.db import models

class ProductoTercero(models.Model):
    nombre = models.CharField(max_length=100)
    tienda = models.CharField(max_length=100)
    precio = models.DecimalField(max_digits=8, decimal_places=2)
    creador = models.ForeignKey('tienda.Vendedor', on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f"{self.nombre} - {self.tienda}"