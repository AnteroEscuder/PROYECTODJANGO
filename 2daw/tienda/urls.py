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
    path('tiendas/<int:idTien>/eliminar/', views.delete_tienda, name='delete_tienda'),
    path('crear-tienda/',views.create_tienda, name='create_tienda'),
    path('medicamentos/<int:idMed>/',views.get_medicamento, name='get_medicamento'),
    path('medicamentos/<int:idMed>/edit',views.edit_medicamento, name='edit_medicamento'),
    path('medicamentos/<int:idMed>/eliminar/', views.delete_medicamento, name='delete_medicamento'),
    path('cuenta/', views.ver_o_crear_cuenta_bancaria, name='ver_cuenta_bancaria'),
    path('cuenta/editar/', views.editar_cuenta_bancaria, name='editar_cuenta_bancaria'),
    path('cuenta/eliminar/', views.eliminar_cuenta_bancaria, name='eliminar_cuenta_bancaria'),
    path('vendedor/datos/', views.ver_datos_vendedor, name='ver_datos_vendedor'),
    path('vendedor/datos/crear/', views.crear_datos_vendedor, name='crear_datos_vendedor'),
    path('vendedor/datos/editar/', views.editar_datos_vendedor, name='editar_datos_vendedor'),
    path('vendedor/datos/eliminar/', views.eliminar_datos_vendedor, name='eliminar_datos_vendedor'),
    path('perfil/', views.ver_perfil, name='ver_perfil'),
]