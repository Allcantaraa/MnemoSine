from django.shortcuts import render
from dashboard.models import Cliente

def index(request) :
    clientes = Cliente.objects.all().order_by('is_vip')
    return render(request, 'index.html', {'clientes': clientes})