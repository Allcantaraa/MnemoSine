from django.shortcuts import render, redirect
from dashboard.models import Cliente, Dashboard
from django.shortcuts import get_object_or_404
from django.contrib import messages
from dashboard.forms import ClienteForm
from django.contrib.auth.decorators import login_required
from django.urls import reverse

def index(request) :
    clientes = Cliente.objects.all().order_by('-is_vip')
    return render(request, 'index.html', {'clientes': clientes})

def dashboards(request, slug) :
    dashboards = Dashboard.objects.filter(client__slug=slug)
    
    return render(request, 'cliente_dashboards.html', {'dashboards': dashboards})

def dashboard(request, slug) :
    dashboard = get_object_or_404(Dashboard, slug=slug)
    
    return render(request, 'detalhes_dashboard.html', {'dashboard': dashboard})

def criar_cliente(request) :
    
    form_action = reverse('criar_cliente')
    
    if request.method == 'POST' :
        form = ClienteForm(request.POST, request.FILES)
        
        if form.is_valid() :
            cliente_criado = form.save()
            cliente_criado.save()
            messages.success(request, 'Cliente criado com sucesso')
            return redirect('index')
        
        return render(request, 'cliente_criar.html', {'form': form, 'form_action': form_action})
            
    
    return render(request, 'cliente_criar.html', {'form': ClienteForm(), 'form_action': form_action})
    

def atualizar_cliente(request, slug) :
    cliente = get_object_or_404(Cliente, slug=slug)
    
    form_action = reverse('atualizar_cliente', args=(slug, ))
    
    if request.method == 'POST' :
        form = ClienteForm(request.POST, request.FILES,instance=cliente)
        
        if form.is_valid() :
            form.save()
            messages.success(request, 'Cliente atualizado com sucesso')
            return redirect('index')
        
        return render(request, 'cliente_criar.html', {'form': form, 'form_action': form_action})
    
    return render(request, 'cliente_criar.html', {'form': ClienteForm(instance=cliente), 'form_action': form_action})

def deletar_cliente(request, slug) :
    cliente = get_object_or_404(Cliente, slug=slug)
    
    confirmation = request.POST.get('confirmation', 'no')
    
    if confirmation == 'yes': 
        cliente.delete()
        return redirect('index')
    
    return render(request, 'modals/deletar_cliente.html', {'cliente': cliente, 'confirmation': confirmation})