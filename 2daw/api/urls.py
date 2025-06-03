from django.urls import path
from .views import *

urlpatterns = [
    path('productos/', productos_terceros_api, name='productos_terceros_api'),
    path('productos/<int:producto_id>/', producto_tercero_detail, name='producto_tercero_detail'),
]
