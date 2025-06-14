from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *

router = DefaultRouter()
router.register(r'medicamentos', MedicamentoViewSet)

urlpatterns = [
    path('productos/', productos_terceros_api, name='productos_terceros_api'),
    path('productos/<int:producto_id>/', producto_tercero_detail, name='producto_tercero_detail'),
    path('', include(router.urls)),
    path('productos-api/', productos_api, name='productos_api'),
]
