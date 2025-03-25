from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name ="inicio"),
    path('clientes/',views.lista_clientes, name='lista_clientes'),
    path('registrar/',views.registrar_usuario, name='registrar_usuario')
]