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


@login_required
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