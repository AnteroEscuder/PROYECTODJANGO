from django.shortcuts import render
from .models import Cliente
# Create your views here.
def lista_clientes(request):
    listado_clientes = Cliente.objects.all()
    return render(request,'clientes/lista_clientes.html',{'cliente_mostrar': listado_clientes})
