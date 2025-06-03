from oauth2_provider.decorators import protected_resource
from django.http import JsonResponse
from .models import ProductoTercero


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