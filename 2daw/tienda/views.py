from datetime import datetime
from django.shortcuts import render, redirect
from .models import Cliente
from .forms import *
from django.contrib.auth import login

# Create your views here.
def index(request):
    if(not "fecha_inicio" in request.session):
      request.session["fecha_inicio"] = datetime.now().strftime('%d/%m/%Y %H:%M')

    return render(request,'index.html',{})

def lista_clientes(request):
    listado_clientes = Cliente.objects.all()
    return render(request,'clientes/lista_clientes.html',{'cliente_mostrar': listado_clientes})

# def registrar_usuario(request):
#    formulario = RegistroForm()
#    return render(request,'registration/signup.html', {'formulario': formulario})

def registrar_usuario(request):
    if request.method == 'POST':
        formulario = RegistroForm(request.POST)
        if formulario.is_valid():
            user = formulario.save() 
            login(request, user)
            return redirect('inicio')
    else:
        formulario = RegistroForm()

    return render(request, 'registration/signup.html', {'formulario': formulario})