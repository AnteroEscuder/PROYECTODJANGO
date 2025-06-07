from oauth2_provider.decorators import protected_resource
from django.http import JsonResponse
from .models import *
from rest_framework import viewsets
from .serializers import MedicamentoSerializer
from rest_framework.permissions import BasePermission


# Create your views here.
def productos_terceros_api(request):
    productos = list(ProductoTercero.objects.values('id', 'nombre', 'tienda', 'precio'))
    return JsonResponse(productos, safe=False)

def producto_tercero_detail(request, producto_id):
    try:
        producto = ProductoTercero.objects.get(pk=producto_id)
        data = {
            'id': producto.id,
            'nombre': producto.nombre,
            'precio': str(producto.precio),
            'tienda': producto.tienda,
        }
        return JsonResponse(data)
    except ProductoTercero.DoesNotExist:
        return JsonResponse({'error': 'Producto no encontrado'}, status=404)

class EsVendedor(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and hasattr(request.user, 'vendedor')

class MedicamentoViewSet(viewsets.ModelViewSet):
    queryset = ProductoTercero.objects.all()
    serializer_class = MedicamentoSerializer
    permission_classes = [EsVendedor]

    def perform_create(self, serializer):
        vendedor = self.request.user.vendedor
        serializer.save(creador=vendedor)
