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
    listado_medicamentos = Medicamento.objects.all()
    return render(request, 'medicamentos/lista_medicamentos.html', {'medicamentos_mostrar' : listado_medicamentos})

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

def get_tienda(request, idTien):
    try:
        tienda = Tienda.objects.get(id=idTien)
    except Tienda.DoesNotExist:
        raise Http404("Tienda no encontrada")
    return render(request, 'tiendas/tienda_view.html', {'tienda': tienda})

def get_medicamento(request, idMed):
    try:
        medicamento = Medicamento.objects.get(id=idMed)
    except Medicamento.DoesNotExist:
        raise Http404("Tienda no encontrada")
    return render(request, 'medicamentos/medicamento_view.html', {'medicamento': medicamento})

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

def error_500_view(request, exception):
    return render(request, 'errores/error_500.html', status=500)

def error_404_view(request, exception):
    return render(request, 'errores/error_404.html', status=404)
