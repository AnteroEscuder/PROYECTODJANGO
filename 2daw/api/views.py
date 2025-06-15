import requests
from oauth2_provider.decorators import protected_resource
from django.http import JsonResponse
from .models import *
from rest_framework import viewsets
from .serializers import MedicamentoSerializer
from rest_framework.permissions import BasePermission
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.models import User
import json
from decimal import Decimal
from tienda.models import Usuario

# from django.contrib.auth import get_user_model
# Usuario = get_user_model()

@csrf_exempt
def productos_terceros_api(request):
    if request.method == "GET":
        nombre = request.GET.get('nombre')
        
        productos = ProductoTercero.objects.all()
        if nombre:
            productos = productos.filter(nombre__icontains=nombre)

        productos = list(productos.values('id', 'nombre', 'descripcion', 'precio', 'fecha_caducidad'))
        return JsonResponse(productos, safe=False)

    elif request.method == "POST":
        try:
            data = json.loads(request.body)

            usuario = Usuario.objects.get(id=data.get('vendedor'))
            if not hasattr(usuario, 'vendedor'):
                return JsonResponse({"error": "Este usuario no es un vendedor."}, status=400)

            vendedor = usuario.vendedor

            nuevo_producto = ProductoTercero.objects.create(
                nombre=data['nombre'],
                descripcion=data['descripcion'],
                precio=Decimal(data['precio']),
                fecha_caducidad=data['fecha_caducidad'],
                vendedor=vendedor
            )
            return JsonResponse({"mensaje": "Producto creado correctamente", "id": nuevo_producto.id}, status=201)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)

    elif request.method == "PUT":
        try:
            data = json.loads(request.body)
            producto_id = data.get("id")
            producto = ProductoTercero.objects.get(id=producto_id)

            producto.nombre = data.get("nombre", producto.nombre)
            producto.descripcion = data.get("descripcion", producto.descripcion)
            producto.precio = Decimal(data.get("precio", producto.precio))
            producto.fecha_caducidad = data.get("fecha_caducidad", producto.fecha_caducidad)
            producto.save()

            return JsonResponse({"mensaje": "Producto actualizado correctamente"}, status=200)

        except ProductoTercero.DoesNotExist:
            return JsonResponse({"error": "Producto no encontrado"}, status=404)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)

    elif request.method == "DELETE":
        try:
            data = json.loads(request.body)
            producto_id = data.get("id")

            if not producto_id:
                return JsonResponse({"error": "ID no proporcionado"}, status=400)

            producto = ProductoTercero.objects.get(id=producto_id)
            producto.delete()

            return JsonResponse({"mensaje": "Producto eliminado correctamente"}, status=200)

        except ProductoTercero.DoesNotExist:
            return JsonResponse({"error": "Producto no encontrado"}, status=404)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)

def producto_tercero_detail(request, producto_id):
    try:
        producto = ProductoTercero.objects.get(pk=producto_id)
        data = {
            'id': producto.id,
            'nombre': producto.nombre,
            'precio': str(producto.precio),
            'descripcion': producto.descripcion,
            'fecha_caducidad': producto.fecha_caducidad,
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
        serializer.save(vendedor=vendedor)

def obtener_token_oauth():
    response = requests.post(
        settings.API_TOKEN_URL,
        data={
            'client_id': settings.API_CLIENT_ID,
            'client_secret': settings.API_CLIENT_SECRET,
            'grant_type': 'client_credentials',
        }
    )
    return response.json().get("access_token")

def productos_api(request):
    try:
        token = obtener_token_oauth()
        headers = {'Authorization': f'Bearer {token}'}
        response = requests.get(settings.API_PRODUCTOS_URL, headers=headers)
        productos = response.json() if response.status_code == 200 else []
    except Exception as e:
        print("ERROR API:", e)
        productos = []

    return render(request, 'api/productos_api.html', {'productos': productos})