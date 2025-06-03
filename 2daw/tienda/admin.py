from django.contrib import admin
from .models import *
admin.site.register(Cliente)
admin.site.register(Vendedor)
admin.site.register(Usuario)
admin.site.register(Inventario)
admin.site.register(Medicamento)
admin.site.register(Tienda)
admin.site.register(Compra)
admin.site.register(Pedido)
admin.site.register(LineaPedido)

# Register your models here.
