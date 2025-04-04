from datetime import datetime
from django.shortcuts import render, redirect
from .models import Cliente, Vendedor, Medicamento
from .forms import *
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import Group
from django.contrib import messages
from django.contrib.auth.decorators import permission_required, user_passes_test

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
    if request.method == 'POST':
        formulario = MedicamentoModelForm(request.POST)

        if formulario.is_valid():
            print("Es valido")
            formulario.save()
            return redirect("lista_medicamentos")

    else:
        formulario = MedicamentoModelForm()
    return render(request, 'medicamentos/medicamentos_form.html',{'formulario': formulario})

@permission_required('tienda.view_tienda')
def lista_tiendas(request):
    listado_tiendas = Tienda.objects.all()
    return render(request, 'tiendas/lista_tiendas.html', {'tiendas_mostrar' : listado_tiendas})

@permission_required('tienda.add_tienda')
def create_tienda(request):
    if request.method == 'POST':
        formulario = TiendaModelForm(request.POST)

        if formulario.is_valid():
            print("Es valido")
            formulario.save()
            return redirect("lista_tiendas")

    else:
        formulario = TiendaModelForm()
    return render(request, 'tiendas/tiendas_form.html',{'formulario': formulario})