from django.urls import include, path
from . import views

urlpatterns = [
    path('', views.index, name ="inicio"),
    path('clientes/',views.lista_clientes, name='lista_clientes'),
    path('registrar/',views.registrar_usuario, name='registrar_usuario'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('vendedores/',views.lista_vendedores, name='lista_vendedores'),
    path('medicamentos/',views.lista_medicamentos, name='lista_medicamentos'),
    path('crear-medicamento/',views.create_medicamento, name='create_medicamento'),
    path('tiendas/',views.lista_tiendas, name='lista_tiendas'),
    path('tiendas/<int:idTien>/',views.get_tienda, name='get_tienda'),
    path('tiendas/<int:idTien>/edit',views.edit_tienda, name='edit_tienda'),
    path('crear-tienda/',views.create_tienda, name='create_tienda'),
    path('medicamentos/<int:idMed>/',views.get_medicamento, name='get_medicamento'),
    path('medicamentos/<int:idMed>/edit',views.edit_medicamento, name='edit_medicamento'),
    
]