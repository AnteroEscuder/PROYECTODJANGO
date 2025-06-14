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
    path('crear/inventario/', views.crear_inventario, name='crear_inventario'),
    path('tienda/<int:id_tienda>/medicamentos/', views.listar_medicamentos_tienda, name='listar_medicamentos_tienda'),
    path('inventario/<int:id>/editar/', views.editar_inventario, name='editar_inventario'),
    path('inventario/<int:id>/eliminar/', views.eliminar_inventario, name='eliminar_inventario'),
    path('pedido/crear/', views.crear_pedido, name='crear_pedido'),
    path('comprar/<int:medicamento_id>', views.comprar_medicamento, name='comprar_medicamento'),
    path('compra/confirmada/', views.confirmar_compra, name='confirmar_compra'),
    path('carrito/anadir/<int:medicamento_id>/<int:tienda_id>/', views.anadir_al_carrito, name='anadir_al_carrito'),
    path('carrito/', views.carrito_view, name='carrito'),
    path('carrito/finalizar/', views.finalizar_compra, name='finalizar_compra'),
    path('carrito/resumen/<int:pedido_id>/', views.resumen_compra, name='resumen_compra'),
    path('productos-terceros/', views.productos_terceros, name='productos_terceros'),
    path('importar-producto/<int:producto_id>/', views.importar_producto, name='importar_producto'),
    path('editar-linea/<int:linea_id>/', views.editar_linea, name='editar_linea'),
    path('eliminar-linea/<int:linea_id>/', views.eliminar_linea, name='eliminar_linea'),
    path('historial/', views.historial_pedidos, name='historial'),
    path('devolver-pedido/<int:pedido_id>/', views.devolver_pedido, name='devolver_pedido'),
    path('productos-pedidos/', views.productos_pedidos_por_clientes, name='productos_pedidos_vendedor'),
    path('devoluciones-pendientes/', views.devoluciones_pendientes, name='devoluciones_pendientes'),
    path('aceptar-devolucion/<int:devolucion_id>/', views.aceptar_devolucion, name='aceptar_devolucion'),
    path('devolver-producto/<int:linea_id>/', views.solicitar_devolucion_producto, name='solicitar_devolucion_producto'),
    path('clientes/<int:cliente_id>/pedidos/', views.pedidos_de_cliente, name='pedidos_de_cliente'),
    path('clientes-con-pedidos/', views.clientes_con_pedidos, name='clientes_con_pedidos'),
    path('pedido/<int:pedido_id>/cancelar/', views.cancelar_pedido, name='cancelar_pedido'),
]

from django.conf.urls import handler404

handler404 = views.error_404_view

handler500 = views.error_500_view