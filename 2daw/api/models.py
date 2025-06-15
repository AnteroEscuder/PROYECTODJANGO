from django.db import models

class ProductoTercero(models.Model):
    nombre = models.CharField(max_length=100)
    precio = models.DecimalField(max_digits=8, decimal_places=2)
    descripcion = models.CharField(max_length=250)
    fecha_caducidad = models.DateField()
    vendedor = models.ForeignKey('tienda.Vendedor', on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f"{self.nombre}"