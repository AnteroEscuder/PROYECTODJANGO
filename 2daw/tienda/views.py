from datetime import datetime
from django.shortcuts import render, redirect
from .models import Cliente, Vendedor, Medicamento, CuentaBancaria
from .forms import *
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import Group
from django.contrib import messages
from django.contrib.auth.decorators import permission_required, user_passes_test
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404
from django.http import HttpResponseForbidden, Http404
from django.utils.timezone import now
import requests
from django.conf import settings
from django.db import transaction
from decimal import Decimal
from django.db import transaction

# Create your views here.
def index(request):
    if(not "fecha_inicio" in request.session):
      request.session["fecha_inicio"] = datetime.now().strftime('%d/%m/%Y %H:%M')

    return render(request,'index.html',{})

@permission_required('tienda.add_cliente')
def lista_clientes(request):
    listado_clientes = Cliente.objects.all()
    return render(request,'clientes/lista_clientes.html',{'cliente_mostrar': listado_clientes})

@permission_required('tienda.view_vendedor')
def lista_vendedores(request):
    listado_vendedores = Vendedor.objects.all()
    return render(request, 'vendedores/lista_vendedores.html', {'vendedores_mostrar' : listado_vendedores})

def is_cliente(user):
    return user.rol == Usuario.CLIENTE

def is_vendedor(user):
    return user.rol == Usuario.VENDEDOR

@permission_required('tienda.view_medicamento')
def lista_medicamentos(request):
    buscar = request.GET.get('buscar', '')
    medicamentos = Medicamento.objects.all()

    if buscar:
        medicamentos = medicamentos.filter(nombre__icontains=buscar)

    return render(request, 'medicamentos/lista_medicamentos.html', {
        'medicamentos_mostrar': medicamentos,
        'buscar': buscar,
    })

def registrar_usuario(request):
    if request.method == 'POST':
        formulario = RegistroForm( request.POST)
        if formulario.is_valid():
            user = formulario.save()
            rol = int(formulario.cleaned_data.get('rol'))
            if(rol == Usuario.CLIENTE):
                grupo = Group.objects.get(name = 'Clientes')
                grupo.user_set.add(user)
                cliente = Cliente.objects.create( usuario = user)
                cliente.save()
            elif(rol == Usuario.VENDEDOR):
                grupo = Group.objects.get(name = 'Vendedores')
                grupo.user_set.add(user)
                vendedor = Vendedor.objects.create( usuario = user)
                vendedor.save()
            login(request, user)
            return redirect('inicio')
    else :
        formulario = RegistroForm()
    return render(request, 'registration/signup.html', {'formulario': formulario})

def logout_view(request):
    logout(request)
    return redirect('inicio')

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)

        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('inicio')
        else:
            messages.error(request, 'Usuario o contraseña incorrectos')
            return redirect('login')
    else:
        form = LoginForm()
    
    return  render(request, 'registration/login.html', {'form': form})

@permission_required('tienda.add_medicamento')
def create_medicamento(request):
    try:
        vendedor = Vendedor.objects.get(usuario=request.user)
    except Vendedor.DoesNotExist:
        raise Http404("Vendedor no encontrado")

    if request.method == 'POST':
        form = MedicamentoModelForm(request.POST)
        if form.is_valid():
            medicamento = form.save(commit=False)
            medicamento.vendedor = vendedor
            medicamento.save()
            messages.success(request, 'Medicamento creado correctamente.')
            return redirect('lista_medicamentos')
    else:
        form = MedicamentoModelForm()

    return render(request, 'medicamentos/medicamento_form.html', {'formulario': form})

@permission_required('tienda.view_tienda')
def lista_tiendas(request):
    listado_tiendas = Tienda.objects.all()
    return render(request, 'tiendas/lista_tiendas.html', {'tiendas_mostrar' : listado_tiendas})

@permission_required('tienda.add_tienda')
def create_tienda(request):
    try:
        vendedor = Vendedor.objects.get(usuario=request.user)
    except Vendedor.DoesNotExist:
        raise Http404("Vendedor no encontrado")

    if request.method == 'POST':
        formulario = TiendaModelForm(request.POST)
        if formulario.is_valid():
            tienda = formulario.save(commit=False)
            tienda.vendedor = vendedor
            tienda.save()
            messages.success(request, 'Tienda creada correctamente.')
            return redirect('lista_tiendas')
    else:
        formulario = TiendaModelForm()

    return render(request, 'tiendas/tiendas_form.html', {'formulario': formulario})

@permission_required('tienda.view_tienda')
def get_tienda(request, idTien):
    try:
        tienda = Tienda.objects.get(id=idTien)
    except Tienda.DoesNotExist:
        raise Http404("Tienda no encontrada")
    return render(request, 'tiendas/tienda_view.html', {'tienda': tienda})

def get_medicamento(request, idMed):
    medicamento = get_object_or_404(Medicamento, id=idMed)
    tiendas = Inventario.objects.filter(medicamento=medicamento)
    return render(request, 'medicamentos/medicamento_view.html', {
        'medicamento': medicamento,
        'tiendas': tiendas,
    })

@permission_required('tienda.add_cuentabancaria')
def ver_o_crear_cuenta_bancaria(request):
    try:
        cliente = Cliente.objects.get(usuario=request.user)
    except Cliente.DoesNotExist:
        raise Http404("Cliente no encontrado")

    try:
        cuenta = CuentaBancaria.objects.get(cliente=cliente)
        return render(request, 'cuenta_bancaria/ver.html', {'cuenta': cuenta})
    except CuentaBancaria.DoesNotExist:
        if request.method == 'POST':
            form = CuentaBancariaForm(request.POST)
            if form.is_valid():
                cuenta = form.save(commit=False)
                cuenta.cliente = cliente
                cuenta.save()
                messages.success(request, 'Datos cuenta bancaria guardados correctamente.')
                return redirect('ver_cuenta_bancaria')
        else:
            form = CuentaBancariaForm()
        return render(request, 'cuenta_bancaria/crear.html', {'form': form})

@permission_required('tienda.change_cuentabancaria')
def editar_cuenta_bancaria(request):
    try:
        cliente = Cliente.objects.get(usuario=request.user)
    except Cliente.DoesNotExist:
        raise Http404("Cliente no encontrado")

    try:
        cuenta = CuentaBancaria.objects.get(cliente=cliente)
    except CuentaBancaria.DoesNotExist:
        raise Http404("Cuenta no encontrado")

    if request.method == 'POST':
        form = CuentaBancariaForm(request.POST, instance=cuenta)
        if form.is_valid():
            form.save()
            return redirect('ver_cuenta_bancaria')
    else:
        form = CuentaBancariaForm(instance=cuenta)
    return render(request, 'cuenta_bancaria/editar.html', {'form': form})

@permission_required('tienda.delete_cuentabancaria')
def eliminar_cuenta_bancaria(request):
    try:
        cliente = Cliente.objects.get(usuario=request.user)
    except Cliente.DoesNotExist:
        raise Http404("Cliente no encontrado")

    try:
        cuenta = CuentaBancaria.objects.get(cliente=cliente)
    except CuentaBancaria.DoesNotExist:
        raise Http404("Cuenta no encontrado")

    if request.method == 'POST':
        cuenta.delete()
        return redirect('ver_cuenta_bancaria')

    return render(request, 'cuenta_bancaria/confirmar_eliminacion.html', {'cuenta': cuenta})

@permission_required('tienda.view_datosvendedor')
def ver_datos_vendedor(request):
    try:
        vendedor = Vendedor.objects.get(usuario=request.user)
        datos = DatosVendedor.objects.get(vendedor=vendedor)
        return render(request, 'datos_vendedor/ver.html', {'datos': datos})
    except (Vendedor.DoesNotExist, DatosVendedor.DoesNotExist):
        return redirect('crear_datos_vendedor')

@permission_required('tienda.add_datosvendedor')
def crear_datos_vendedor(request):
    try:
        vendedor = Vendedor.objects.get(usuario=request.user)
    except Vendedor.DoesNotExist:
        raise Http404("Vendedor no encontrado")

    if DatosVendedor.objects.filter(vendedor=vendedor).exists():
        return redirect('ver_datos_vendedor')

    if request.method == 'POST':
        formulario = DatosVendedorForm(request.POST)
        if formulario.is_valid():
            datos = formulario.save(commit=False)
            datos.vendedor = vendedor
            datos.save()
            messages.success(request, 'Datos del vendedor guardados correctamente.')
            return redirect('ver_datos_vendedor')
    else:
        formulario = DatosVendedorForm()

    return render(request, 'datos_vendedor/crear.html', {'form': formulario})

@permission_required('tienda.change_datosvendedor')
def editar_datos_vendedor(request):
    try:
        vendedor = Vendedor.objects.get(usuario=request.user)
    except Vendedor.DoesNotExist:
        raise Http404("Vendedor no encontrado")

    try:
        datos = DatosVendedor.objects.get(vendedor=vendedor)
    except DatosVendedor.DoesNotExist:
        raise Http404("Datos delvendedor no encontrados")

    if request.method == 'POST':
        formulario = DatosVendedorForm(request.POST, instance=datos)
        if formulario.is_valid():
            formulario.save()
            messages.success(request, 'Datos actualizados correctamente.')
            return redirect('ver_datos_vendedor')
    else:
        formulario = DatosVendedorForm(instance=datos)

    return render(request, 'datos_vendedor/editar.html', {'form': formulario})

@permission_required('tienda.delete_datosvendedor')
def eliminar_datos_vendedor(request):
    try:
        vendedor = Vendedor.objects.get(usuario=request.user)
    except Vendedor.DoesNotExist:
        raise Http404("Vendedor no encontrado")

    try:
        datos = DatosVendedor.objects.get(vendedor=vendedor)
    except DatosVendedor.DoesNotExist:
        raise Http404("Datos delvendedor no encontrados")

    if request.method == 'POST':
        datos.delete()
        messages.success(request, 'Datos eliminados correctamente.')
        return redirect('crear_datos_vendedor')

    return render(request, 'datos_vendedor/confirmar_eliminacion.html', {'datos': datos})

def ver_perfil(request):
    usuario = request.user

    if usuario.rol == Usuario.CLIENTE:
        return redirect('ver_cuenta_bancaria')
    elif usuario.rol == Usuario.VENDEDOR:
        return redirect('ver_datos_vendedor')
    else:
        return render(request, 'error.html', {'mensaje': 'Rol no reconocido'})

@permission_required('tienda.change_medicamento')
def edit_medicamento(request, idMed):
    try:
        vendedor = Vendedor.objects.get(usuario=request.user)
    except Vendedor.DoesNotExist:
        raise Http404("Vendedor no encontrado")

    try:
        medicamento = get_object_or_404(Medicamento, id=idMed, vendedor=vendedor)
    except Medicamento.DoesNotExist:
        raise Http404("Medicamento no encontrados")

    if request.method == 'POST':
        form = MedicamentoModelForm(request.POST, instance=medicamento)
        if form.is_valid():
            form.save()
            messages.success(request, 'Medicamento actualizado correctamente.')
            return redirect('get_medicamento', idMed=idMed)
    else:
        form = MedicamentoModelForm(instance=medicamento)

    return render(request, 'medicamentos/medicamento_edit.html', {'edit_medicamento': form, 'medicamento_edited': medicamento})

@permission_required('tienda.delete_medicamento')
def delete_medicamento(request, idMed):
    try:
        vendedor = Vendedor.objects.get(usuario=request.user)
    except Vendedor.DoesNotExist:
        raise Http404("Vendedor no encontrado")

    try:
        medicamento = get_object_or_404(Medicamento, id=idMed, vendedor=vendedor)
    except Medicamento.DoesNotExist:
        raise Http404("Medicamento no encontrados")

    if request.method == 'POST':
        medicamento.delete()
        messages.success(request, 'Medicamento eliminado correctamente.')
        return redirect('lista_medicamentos')

    return render(request, 'medicamentos/medicamento_confirm_delete.html', {'medicamento': medicamento})

@permission_required('tienda.change_tienda')
def edit_tienda(request, idTien):

    try:
        vendedor = Vendedor.objects.get(usuario=request.user)
    except Vendedor.DoesNotExist:
        raise Http404("Vendedor no encontrado")

    try:
        tienda = get_object_or_404(Tienda, id=idTien, vendedor=vendedor)
    except Tienda.DoesNotExist:
        raise Http404("Tienda no encontrada")

    if request.method == 'POST':
        formulario = TiendaModelForm(request.POST, instance=tienda)
        if formulario.is_valid():
            formulario.save()
            messages.success(request, 'Tienda actualizada correctamente.')
            return redirect('get_tienda', idTien=tienda.id)
    else:
        formulario = TiendaModelForm(instance=tienda)

    return render(request, 'tiendas/tienda_edit.html', {'edit_tienda': formulario, 'tienda_edited': tienda})

@permission_required('tienda.delete_tienda')
def delete_tienda(request, idTien):

    try:
        vendedor = Vendedor.objects.get(usuario=request.user)
    except Vendedor.DoesNotExist:
        raise Http404("Vendedor no encontrado")

    try:
        tienda = get_object_or_404(Tienda, id=idTien, vendedor=vendedor)
    except Tienda.DoesNotExist:
        raise Http404("Tienda no encontrada")

    if request.method == 'POST':
        tienda.delete()
        messages.success(request, 'Tienda eliminada correctamente.')
        return redirect('lista_tiendas')

    return render(request, 'tiendas/tienda_confirm_delete.html', {'tienda': tienda})

@permission_required('tienda.add_inventario')
def crear_inventario(request):
    if request.method == 'POST':
        formulario = InventarioModelForm(request.POST, request=request)
        if formulario.is_valid():
            inventario = Inventario.objects.filter(
                tienda=formulario.cleaned_data['tienda'],
                medicamento=formulario.cleaned_data['medicamento']
            ).first()
            if inventario is None:
                formulario.save()
            else:
                inventario.cantidad += formulario.cleaned_data['cantidad']
                inventario.save()
            messages.success(request, 'Medicamento añadido o actualizado en la tienda.')
            return redirect('lista_tiendas')
    else:
        formulario = InventarioModelForm(None, request=request)

    return render(request, 'inventario/inventario_form.html', {'crear_inventario': formulario})

@permission_required('tienda.view_inventario')
def listar_medicamentos_tienda(request, id_tienda):
    tienda = get_object_or_404(Tienda, id=id_tienda)
    buscar = request.GET.get("buscar", "")
    inventario = Inventario.objects.filter(tienda=tienda)

    if buscar:
        inventario = inventario.filter(medicamento__nombre__icontains=buscar)

    return render(request, 'inventario/listar_inventario.html', {
        'tienda': tienda,
        'inventario': inventario,
        'buscar': buscar
    })

@permission_required('tienda.change_inventario')
def editar_inventario(request, id):
    inventario = get_object_or_404(Inventario, id=id)

    if request.method == 'POST':
        form = InventarioModelForm(request.POST, instance=inventario, request=request)        
        if form.is_valid():
            form.save()
            messages.success(request, "Cantidad modificada correctamente.")
            return redirect('listar_medicamentos_tienda', id_tienda=inventario.tienda.id)
    else:
        form = InventarioModelForm(instance=inventario)

    return render(request, 'inventario/editar_inventario.html', {'form': form, 'inventario': inventario})

@permission_required('tienda.delete_inventario')
def eliminar_inventario(request, id):
    inventario = get_object_or_404(Inventario, id=id)

    if request.method == 'POST':
        inventario.delete()
        messages.success(request, "Producto eliminado de la tienda.")
        return redirect('listar_medicamentos_tienda', id_tienda=inventario.tienda.id)

    return render(request, 'inventario/eliminar_inventario.html', {'inventario': inventario})

@permission_required('tienda.add_pedido')
def crear_pedido(request):
    cliente = get_object_or_404(Cliente, usuario=request.user)

    if request.method == 'POST':
        form = PedidoForm(request.POST)
        if form.is_valid():
            pedido = form.save(commit=False)
            pedido.cliente = cliente
            pedido.save()
            form.save_m2m()
            messages.success(request, "Pedido realizado correctamente.")
            return redirect('inicio')
    else:
        form = PedidoForm()

    return render(request, 'pedidos/crear_pedido.html', {'form': form})

def comprar_medicamento(request, medicamento_id):
    medicamento = get_object_or_404(Medicamento, id=medicamento_id)
    precio = None

    if request.method == 'POST':
        form = CompraForm(medicamento, request.POST)
        if form.is_valid():
            tienda = form.cleaned_data['tienda']
            cantidad = form.cleaned_data['cantidad']
            inventario = Inventario.objects.get(tienda=tienda, medicamento=medicamento)

            if inventario.cantidad < cantidad:
                form.add_error('cantidad', f'Solo hay {inventario.cantidad} unidades disponibles.')
            else:
                inventario.cantidad -= cantidad
                inventario.save()

                cliente = Cliente.objects.get(usuario=request.user)
             
                Compra.objects.create(
                    cliente=cliente,
                    tienda=tienda,
                    medicamento=medicamento,
                    cantidad=cantidad,
                    # TODO meter esto en la DB
                    precio_unitario=inventario.precio
                )
                return redirect('confirmar_compra')

        else:
            tienda = request.POST.get('tienda')
            if tienda:
                inventario = Inventario.objects.filter(tienda=tienda, medicamento=medicamento).first()
                if inventario:
                    precio = inventario.precio

    else:
        form = CompraForm(medicamento)
        primera_tienda = form.fields['tienda'].queryset.first()
        if primera_tienda:
            inventario = Inventario.objects.filter(tienda=primera_tienda, medicamento=medicamento).first()
            if inventario:
                precio = inventario.precio

    return render(request, 'tiendas/comprar_medicamento.html', {
        'medicamento': medicamento,
        'form': form,
        'precio': precio
    })

@permission_required('tienda.add_pedido')
def anadir_al_carrito(request, medicamento_id, tienda_id):
    cliente = get_object_or_404(Cliente, usuario=request.user)
    medicamento = get_object_or_404(Medicamento, pk=medicamento_id)
    tienda = get_object_or_404(Tienda, pk=tienda_id)
    inventario = get_object_or_404(Inventario, medicamento=medicamento, tienda=tienda)

    if request.method == "POST":
        form = AñadirAlCarritoForm(request.POST)
        if form.is_valid():
            cantidad = form.cleaned_data['cantidad']

            if inventario.cantidad >= cantidad:
                pedido, _ = Pedido.objects.get_or_create(cliente=cliente, fecha__isnull=True)

                linea = LineaPedido.objects.filter(pedido=pedido, medicamento=medicamento, tienda=tienda).first()
                if linea:
                    linea.cantidad += cantidad
                    linea.save()
                else:
                    LineaPedido.objects.create(pedido=pedido, medicamento=medicamento, cantidad=cantidad, tienda=tienda)

                messages.success(request, "Producto añadido al carrito.")
            else:
                messages.error(request, "Stock insuficiente.")
            return redirect('lista_medicamentos')
    else:
        form = AñadirAlCarritoForm(initial={'tienda': tienda})

    return render(request, 'carrito/anadir_al_carrito.html', {
        'medicamento': medicamento,
        'form': form,
        'tienda': tienda
    })



@permission_required('tienda.view_pedido')
def carrito_view(request):
    cliente = get_object_or_404(Cliente, usuario=request.user)
    pedido = Pedido.objects.filter(cliente=cliente, fecha__isnull=True).first()
    lineas = pedido.lineas.all() if pedido else []
    
    total = sum(linea.medicamento.precio * linea.cantidad for linea in lineas)
    tiene_lineas = lineas.exists() if pedido else False

    return render(request, 'carrito/carrito.html', {
        'pedido': pedido,
        'lineas': lineas,
        'total': total,
        'tiene_lineas': tiene_lineas,
    })

@permission_required('tienda.add_pedido')
def finalizar_compra(request):
    cliente = get_object_or_404(Cliente, usuario=request.user)
    cuenta = get_object_or_404(CuentaBancaria, cliente=cliente)
    pedido = Pedido.objects.filter(cliente=cliente, fecha__isnull=True).first()

    if not pedido:
        messages.warning(request, "No tienes ningún pedido en curso.")
        return redirect('carrito')

    lineas = pedido.lineas.all()
    total = sum(linea.medicamento.precio * linea.cantidad for linea in lineas)

    with transaction.atomic():
        for linea in lineas:
            try:
                inventario = Inventario.objects.filter(medicamento=linea.medicamento, tienda=linea.tienda).first()
            except Inventario.DoesNotExist:
                messages.error(request, f"No hay inventario del medicamento {linea.medicamento}.")
                return redirect('carrito')

            if inventario.cantidad < linea.cantidad:
                messages.error(request, f"Stock insuficiente para {linea.medicamento.nombre}.")
                return redirect('carrito')

            inventario.cantidad -= linea.cantidad
            inventario.save()

        pedido.fecha = timezone.now()
        pedido.save()

        if cuenta.saldo > 0:
            if total <= cuenta.saldo:
                cuenta.saldo -= Decimal(total)
                total_pagado = Decimal('0.00')
            else:
                total_pagado = Decimal(total) - cuenta.saldo
                cuenta.saldo = Decimal('0.00')
            cuenta.save()
        else:
            total_pagado = Decimal(total)

    messages.success(request, f"Compra finalizada. Has pagado {total_pagado} €.")
    return redirect('inicio')

@permission_required('tienda.add_pedido')
def resumen_compra(request, pedido_id):
    cliente = get_object_or_404(Cliente, usuario=request.user)
    pedido = get_object_or_404(Pedido, id=pedido_id, cliente=cliente)

    return render(request, 'carrito/resumen_compra.html', {
        'pedido': pedido
    })

@permission_required('tienda.change_pedido')
def devolver_pedido(request, pedido_id):
    pedido = get_object_or_404(Pedido, id=pedido_id, cliente__usuario=request.user)

    for linea in pedido.lineas.all():
        if not Devolucion.objects.filter(linea_pedido=linea).exists():
            Devolucion.objects.create(
                linea_pedido=linea,
                cantidad_devuelta=linea.cantidad,
                aceptado=False
            )

    messages.success(request, "Solicitud de devolución enviada. Pendiente de aprobación por el vendedor.")
    return redirect('historial')

@permission_required('tienda.add_pedido')
def historial_pedidos(request):
    cliente = get_object_or_404(Cliente, usuario=request.user)
    pedidos = Pedido.objects.filter(cliente=cliente, fecha__isnull=False)

    for pedido in pedidos:
        lineas = pedido.lineas.all()
        pedido.total = sum(linea.medicamento.precio * linea.cantidad for linea in lineas)
        pedido.medicamentos = [linea.medicamento.nombre for linea in lineas]

    return render(request, 'carrito/historial.html', {'pedidos': pedidos})

@permission_required('tienda.add_lineapedido')
def editar_linea(request, linea_id):
    linea = get_object_or_404(LineaPedido, id=linea_id)

    try:
        inventario = Inventario.objects.filter(medicamento=linea.medicamento, tienda=linea.tienda).first()
        stock_disponible = inventario.cantidad
    except Inventario.DoesNotExist:
        stock_disponible = 0

    if request.method == 'POST':
        nueva_cantidad = int(request.POST.get('cantidad'))
        cantidad_actual = linea.cantidad
        diferencia = nueva_cantidad - cantidad_actual

        if nueva_cantidad < 1:
            messages.error(request, 'Cantidad no válida.')
        elif diferencia > stock_disponible:
            messages.error(request, f'No hay suficiente stock. Máximo disponible: {stock_disponible}')
        else:
            with transaction.atomic():
                linea.cantidad = nueva_cantidad
                linea.save()

            messages.success(request, 'Cantidad actualizada.')
            return redirect('carrito')

    return render(request, 'carrito/editar_linea.html', {
        'linea': linea,
        'stock_disponible': stock_disponible
    })

@permission_required('tienda.delete_lineapedido')
def eliminar_linea(request, linea_id):
    linea = get_object_or_404(LineaPedido, id=linea_id)

    try:
        inventario = Inventario.objects.get(medicamento=linea.medicamento)
    except Inventario.DoesNotExist:
        inventario = None

    with transaction.atomic():
        if inventario:
            inventario.cantidad += linea.cantidad
            inventario.save()

        linea.delete()

    messages.success(request, 'Producto eliminado del carrito.')
    return redirect('carrito')


def obtener_token_oauth():
    response = requests.post(f'{settings.API_URL}/o/token/', data={
        'grant_type': 'password',
        'username': settings.API_USERNAME,
        'password': settings.API_PASSWORD,
        'client_id': settings.API_CLIENT_ID,
        'client_secret': settings.API_CLIENT_SECRET,
    })
    return response.json().get('access_token')

@permission_required('api.add_productotercero')
def productos_terceros(request):
    vendedor = get_object_or_404(Vendedor, usuario=request.user)
    medicamentos_importados = Medicamento.objects.filter(vendedor=vendedor).values_list('nombre', flat=True)

    token = obtener_token_oauth()
    headers = {'Authorization': f'Bearer {token}'}
    response = requests.get(f"{settings.API_URL}/api/productos/", headers=headers)

    productos = []
    if response.status_code == 200:
        productos = response.json()

    nombres_importados = list(medicamentos_importados)

    return render(request, "productos_terceros.html", {
        "productos": productos,
        "importados": nombres_importados
    })

@permission_required('tienda.add_medicamento')
def importar_producto(request, producto_id):
    vendedor = get_object_or_404(Vendedor, usuario=request.user)
    
    token = obtener_token_oauth()
    headers = {'Authorization': f'Bearer {token}'}
    
    response = requests.get(f"{settings.API_URL}/api/productos/{producto_id}/", headers=headers)
    if response.status_code != 200:
        messages.error(request, "No se pudo obtener el producto.")
        return redirect('productos_terceros')

    producto_data = response.json()

    if Medicamento.objects.filter(nombre=producto_data['nombre'], vendedor=vendedor).exists():
        messages.warning(request, "Este producto ya ha sido importado.")
        return redirect('productos_terceros')

    nuevo_medicamento = Medicamento.objects.create(
        nombre=producto_data.get('nombre', 'Sin nombre'),
        descripcion=producto_data.get('descripcion', 'Sin descripción'),
        precio=int(float(producto_data.get('precio', 0))),
        fecha_caducidad=producto_data.get('fecha_caducidad', '2099-12-31'),
        vendedor=vendedor
    )

    tienda = Tienda.objects.filter(vendedor=vendedor).first()
    if tienda:
        Inventario.objects.create(
            tienda=tienda,
            medicamento=medicamento,
            cantidad=10,
            precio=medicamento.precio
        )

    messages.success(request, "Producto importado correctamente.")
    return redirect('productos_terceros')

@permission_required('tienda.view_pedido')
def productos_pedidos_por_clientes(request):
    vendedor = get_object_or_404(Vendedor, usuario=request.user)
    medicamentos_vendedor = Medicamento.objects.filter(vendedor=vendedor)

    lineas = LineaPedido.objects.filter(medicamento__in=medicamentos_vendedor).select_related('medicamento', 'pedido__cliente__usuario')

    return render(request, 'vendedores/productos_pedidos_por_clientes.html', {
        'lineas': lineas
    })

@permission_required('tienda.view_pedido')
def devoluciones_pendientes(request):
    vendedor = get_object_or_404(Vendedor, usuario=request.user)
    devoluciones = Devolucion.objects.filter(
        linea_pedido__medicamento__vendedor=vendedor,
        aceptado=False
    )
    return render(request, 'clientes/devoluciones_pendientes.html', {
        'devoluciones': devoluciones
    })

@permission_required('tienda.view_pedido')
def aceptar_devolucion(request, devolucion_id):
    devolucion = get_object_or_404(Devolucion, id=devolucion_id, aceptado=False)
    linea = devolucion.linea_pedido
    cliente = linea.pedido.cliente
    cuenta = get_object_or_404(CuentaBancaria, cliente=cliente)

    with transaction.atomic():
        inventario = Inventario.objects.get(medicamento=linea.medicamento)
        inventario.cantidad += devolucion.cantidad_devuelta
        inventario.save()

        total_devolver = devolucion.cantidad_devuelta * linea.medicamento.precio
        cuenta.saldo += total_devolver
        cuenta.save()

        devolucion.aceptado = True
        devolucion.fecha_aceptacion = timezone.now()
        devolucion.save()

        messages.success(request, 'Devolución aceptada y saldo actualizado.')
        return redirect('devoluciones_pendientes')

@permission_required('tienda.add_lineapedido')
def solicitar_devolucion_producto(request, linea_id):
    linea = get_object_or_404(LineaPedido, id=linea_id, pedido__cliente__usuario=request.user)

    if request.method == 'POST':
        cantidad = int(request.POST.get('cantidad'))

        if cantidad > linea.cantidad or cantidad <= 0:
            messages.error(request, "Cantidad no válida.")
        else:
            Devolucion.objects.create(
                linea_pedido=linea,
                cantidad_devuelta=cantidad,
                aceptado=False
            )
            messages.success(request, "Solicitud de devolución enviada.")
            return redirect('historial')

    return render(request, 'carrito/solicitar_devolucion_producto.html', {
        'linea': linea
    })

@permission_required('tienda.add_pedido')
def confirmar_compra(request):
    return render(request, 'tiendas/confirmar_compra.html')

def error_500_view(request, exception):
    return render(request, 'errores/error_500.html', status=500)

def error_404_view(request, exception):
    return render(request, 'errores/error_404.html', status=404)

