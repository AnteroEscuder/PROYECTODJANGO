from datetime import datetime
from django.shortcuts import render
from .models import Cliente
from .forms import *

# Create your views here.
def index(request):
    if(not "fecha_inicio" in request.session):
      request.session["fecha_inicio"] = datetime.now().strftime('%d/%m/%Y %H:%M')

    return render(request,'index.html',{})

def lista_clientes(request):
    listado_clientes = Cliente.objects.all()
    return render(request,'clientes/lista_clientes.html',{'cliente_mostrar': listado_clientes})

def registrar_usuario(request):
   formulario = RegistroForm()
   return render(request,'registration/signup.html', {'formulario': formulario})
