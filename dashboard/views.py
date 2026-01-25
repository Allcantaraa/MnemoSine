from django.shortcuts import render, redirect
from dashboard.models import Cliente, Dashboard, Categoria
from django.shortcuts import get_object_or_404
from django.contrib import messages
from dashboard.forms import ClienteForm, CategoriaForm
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.contrib.auth.decorators import login_required

@login_required()
def index(request) :
    clientes = Cliente.objects.filter(owner=request.user).order_by('-is_vip')
    return render(request, 'index.html', {'clientes': clientes})

@login_required()
def dashboards(request, slug) :
    cliente = get_object_or_404(Cliente, slug=slug, owner=request.user)
    dashboards = Dashboard.objects.filter(client=cliente)
    categorias = Categoria.objects.filter(owner=request.user)
    
    return render(request, 'cliente_dashboards.html', {'dashboards': dashboards, 'client_slug': slug, 'categorias': categorias})

@login_required()
def dashboard(request, slug) :
    dashboard = get_object_or_404(Dashboard, slug=slug)
    
    return render(request, 'detalhes_dashboard.html', {'dashboard': dashboard})

@login_required()
def criar_cliente(request) :
    
    form_action = reverse('criar_cliente')
    
    if request.method == 'POST' :
        form = ClienteForm(request.POST, request.FILES)
        
        if form.is_valid() :
            cliente_criado = form.save(commit=False)
            cliente_criado.owner = request.user
            cliente_criado.save()
            messages.success(request, 'Cliente criado com sucesso')
            return redirect('index')
        
        return render(request, 'cliente_criar.html', {'form': form, 'form_action': form_action})
            
    
    return render(request, 'cliente_criar.html', {'form': ClienteForm(), 'form_action': form_action})
    
@login_required()
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

@login_required()
def deletar_cliente(request, slug) :
    cliente = get_object_or_404(Cliente, slug=slug)
    
    confirmation = request.POST.get('confirmation', 'no')
    
    if confirmation == 'yes': 
        cliente.delete()
        return redirect('index')
    
    return render(request, 'modals/deletar_cliente.html', {'cliente': cliente, 'confirmation': confirmation})

@login_required()
def criar_categoria(request, client_slug) :
    form_action = reverse('criar_categoria', args=(client_slug, ))
    
    if request.method == 'POST' :
        form = CategoriaForm(request.POST)
        
        if form.is_valid() :
            categoria_criada = form.save(commit=False)
            categoria_criada.owner = request.user
            categoria_criada.save()
            messages.success(request, 'Categoria criada com sucesso')
            return redirect('cliente_dashboard', slug=client_slug)
        
        return render(request, 'modals/categoria.html', {'form': form, 'form_action': form_action})
            
    
    return render(request, 'modals/categoria.html', {'form': CategoriaForm(), 'form_action': form_action})

@login_required()
def atualizar_categoria(request, categoria_slug,client_slug) :
    categoria = get_object_or_404(Categoria, slug=categoria_slug)
    form_action = reverse('atualizar_categoria', args=(client_slug, categoria_slug))
    
    if request.method == 'POST' :
        form = CategoriaForm(request.POST, instance=categoria)
        
        if form.is_valid() :
            form.save()
            messages.success(request, 'Categoria atualizada com sucesso')
            return redirect('cliente_dashboard', slug=client_slug)
        
        return render(request, 'modals/categoria.html', {'form': form, 'form_action': form_action})
            
    
    return render(request, 'modals/categoria.html', {'form': CategoriaForm(instance=categoria), 'form_action': form_action})

@login_required()
def deletar_categoria(request, client_slug, categoria_slug) :
    categoria = get_object_or_404(Categoria, slug=categoria_slug)
    
    confirmation = request.POST.get('confirmation', 'no')
    
    if confirmation == 'yes': 
        categoria.delete()
        return redirect('cliente_dashboard', slug=client_slug)
    
    return render(request, 'modals/deletar_categoria.html', {'categoria': categoria, 'confirmation': confirmation, 'client_slug' : client_slug})