from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.db.models import Q

from dashboard.models import Cliente, Dashboard, Categoria, OrganizationMember
from dashboard.forms import ClienteForm, CategoriaForm, DashboardForm
from dashboard.decorators import organization_required, organization_member_or_admin_required, organization_admin_required

@login_required
@organization_required
def index(request):
    """Página principal com KPIs, clientes e filtros."""
    org = request.organization

    # Filtros
    search_query = request.GET.get('search', '').strip()
    category_filter = request.GET.get('category', '')

    # KPIs
    total_clientes = Cliente.objects.filter(organization=org).count()
    total_dashboards = Dashboard.objects.filter(organization=org).count()
    membros_count = OrganizationMember.objects.filter(organization=org).count()

    # Clientes
    clientes = Cliente.objects.filter(organization=org).order_by('-created_at')

    # Categorias para filtro
    categorias = Categoria.objects.filter(organization=org)

    # Filtrar dashboards por categoria se selecionado
    dashboards_qs = Dashboard.objects.filter(organization=org)

    if category_filter:
        try:
            category = Categoria.objects.get(id=category_filter, organization=org)
            dashboards_qs = dashboards_qs.filter(category=category)
        except Categoria.DoesNotExist:
            pass

    # Filtrar por texto (título)
    if search_query:
        dashboards_qs = dashboards_qs.filter(title__icontains=search_query)

    return render(request, 'index.html', {
        'clientes': clientes,
        'dashboards': dashboards_qs,
        'categorias': categorias,
        'total_clientes': total_clientes,
        'total_dashboards': total_dashboards,
        'membros_count': membros_count,
        'search_query': search_query,
        'selected_category': category_filter,
        'organization': org
    })


@login_required
@organization_required
def dashboards(request, slug):
    """Lista dashboards de um cliente específico."""
    org = request.organization
    cliente = get_object_or_404(Cliente, slug=slug, organization=org)
    
    # Filtro de categoria
    category_filter = request.GET.get('category', '')
    
    dashboards_qs = Dashboard.objects.filter(client=cliente)
    
    if category_filter:
        try:
            category = Categoria.objects.get(id=category_filter, organization=org)
            dashboards_qs = dashboards_qs.filter(category=category)
        except Categoria.DoesNotExist:
            pass
    
    categorias = Categoria.objects.filter(organization=org)

    return render(request, 'cliente_dashboards.html', {
        'dashboards': dashboards_qs,
        'client_slug': slug,
        'categorias': categorias,
        'cliente': cliente,
        'selected_category': category_filter
    })


@login_required
@organization_required
def dashboard(request, slug):
    """Visualiza detalhes de um dashboard."""
    org = request.organization
    dashboard_obj = get_object_or_404(Dashboard, slug=slug, organization=org)
    cliente_slug = dashboard_obj.client.slug if dashboard_obj.client else None

    return render(request, 'detalhes_dashboard.html', {
        'dashboard': dashboard_obj,
        'client_slug': cliente_slug
    })


@login_required
@organization_member_or_admin_required
def criar_cliente(request):
    """Cria um novo cliente."""
    org = request.organization
    form_action = reverse('criar_cliente')

    if request.method == 'POST':
        form = ClienteForm(request.POST, request.FILES)

        if form.is_valid():
            cliente_criado = form.save(commit=False)
            cliente_criado.organization = org
            cliente_criado.save()
            messages.success(request, 'Cliente criado com sucesso')
            return redirect('index')

        return render(request, 'cliente_criar.html', {'form': form, 'form_action': form_action})

    return render(request, 'cliente_criar.html', {'form': ClienteForm(), 'form_action': form_action})


@login_required
@organization_member_or_admin_required
def atualizar_cliente(request, slug):
    """Atualiza um cliente existente."""
    org = request.organization
    cliente = get_object_or_404(Cliente, slug=slug, organization=org)

    form_action = reverse('atualizar_cliente', args=(slug,))

    if request.method == 'POST':
        form = ClienteForm(request.POST, request.FILES, instance=cliente)

        if form.is_valid():
            form.save()
            messages.success(request, 'Cliente atualizado com sucesso')
            return redirect('index')

        return render(request, 'cliente_criar.html', {'form': form, 'form_action': form_action})

    return render(request, 'cliente_criar.html', {'form': ClienteForm(instance=cliente), 'form_action': form_action})


@login_required
@organization_admin_required
def deletar_cliente(request, slug):
    """Deleta um cliente (apenas admin)."""
    org = request.organization
    cliente = get_object_or_404(Cliente, slug=slug, organization=org)

    confirmation = request.POST.get('confirmation', 'no')

    if confirmation == 'yes':
        cliente.delete()
        return redirect('index')

    return render(request, 'modals/deletar_cliente.html', {'cliente': cliente, 'confirmation': confirmation})


@login_required
@organization_member_or_admin_required
def criar_categoria(request, client_slug):
    """Cria uma nova categoria."""
    org = request.organization
    # Validar que o cliente existe e pertence à org
    cliente = get_object_or_404(Cliente, slug=client_slug, organization=org)

    form_action = reverse('criar_categoria', args=(client_slug,))

    if request.method == 'POST':
        form = CategoriaForm(request.POST)

        if form.is_valid():
            categoria_criada = form.save(commit=False)
            categoria_criada.organization = org
            categoria_criada.save()
            messages.success(request, 'Categoria criada com sucesso')
            return redirect('cliente_dashboard', slug=client_slug)

        return render(request, 'modals/categoria.html', {'form': form, 'form_action': form_action})

    return render(request, 'modals/categoria.html', {'form': CategoriaForm(), 'form_action': form_action})


@login_required
@organization_member_or_admin_required
def atualizar_categoria(request, categoria_slug, client_slug):
    """Atualiza uma categoria."""
    org = request.organization
    categoria = get_object_or_404(Categoria, slug=categoria_slug, organization=org)
    form_action = reverse('atualizar_categoria', args=(client_slug, categoria_slug))

    if request.method == 'POST':
        form = CategoriaForm(request.POST, instance=categoria)

        if form.is_valid():
            form.save()
            messages.success(request, 'Categoria atualizada com sucesso')
            return redirect('cliente_dashboard', slug=client_slug)

        return render(request, 'modals/categoria.html', {'form': form, 'form_action': form_action})

    return render(request, 'modals/categoria.html', {'form': CategoriaForm(instance=categoria), 'form_action': form_action})


@login_required
@organization_admin_required
def deletar_categoria(request, client_slug, categoria_slug):
    """Deleta uma categoria (apenas admin)."""
    org = request.organization
    categoria = get_object_or_404(Categoria, slug=categoria_slug, organization=org)

    confirmation = request.POST.get('confirmation', 'no')

    if confirmation == 'yes':
        categoria.delete()
        return redirect('cliente_dashboard', slug=client_slug)

    return render(request, 'modals/deletar_categoria.html', {
        'categoria': categoria,
        'confirmation': confirmation,
        'client_slug': client_slug
    })


@login_required
@organization_member_or_admin_required
def criar_dashboard(request, client_slug):
    """Cria um novo dashboard."""
    org = request.organization
    cliente = get_object_or_404(Cliente, slug=client_slug, organization=org)

    form_action = reverse('criar_dashboard', args=(client_slug,))

    if request.method == 'POST':
        form = DashboardForm(request.POST, request.FILES, organization=org)

        if form.is_valid():
            dashboard = form.save(commit=False)
            dashboard.organization = org
            dashboard.client = cliente
            dashboard.save()
            messages.success(request, 'Dashboard criado com sucesso')
            return redirect('cliente_dashboard', slug=client_slug)

        return render(request, 'modals/dashboard.html', {
            'form': form,
            'cliente': cliente,
            'form_action': form_action,
            'is_updating': False
        })

    return render(request, 'modals/dashboard.html', {
        'form': DashboardForm(organization=org),
        'cliente': cliente,
        'form_action': form_action,
        'is_updating': False
    })


@login_required
@organization_member_or_admin_required
def atualizar_dashboard(request, client_slug, slug):
    """Atualiza um dashboard existente."""
    org = request.organization
    dashboard = get_object_or_404(Dashboard, slug=slug, organization=org)

    if dashboard.client.slug != client_slug:
        messages.error(request, "Acesso negado ou cliente inválido.")
        return redirect('index')

    form_action = reverse('atualizar_dashboard', args=(client_slug, slug))

    if request.method == 'POST':
        form = DashboardForm(request.POST, request.FILES, instance=dashboard, organization=org)

        if form.is_valid():
            form.save()
            messages.success(request, f'Dashboard "{dashboard.title}" atualizado com sucesso!')
            return redirect('cliente_dashboard', slug=client_slug)

        return render(request, 'modals/dashboard.html', {
            'form': form,
            'client_slug': client_slug,
            'dashboard': dashboard,
            'form_action': form_action,
            'is_updating': True
        })

    form = DashboardForm(instance=dashboard, organization=org)

    return render(request, 'modals/dashboard.html', {
        'form': form,
        'client_slug': client_slug,
        'dashboard': dashboard,
        'form_action': form_action,
        'is_updating': True
    })


@login_required
@organization_admin_required
def deletar_dashboard(request, client_slug, dashboard_slug):
    """Deleta um dashboard (apenas admin)."""
    org = request.organization
    dashboard = get_object_or_404(Dashboard, slug=dashboard_slug, organization=org, client__slug=client_slug)

    confirmation = request.POST.get('confirmation', 'no')

    if confirmation == 'yes':
        dashboard.delete()
        return redirect('cliente_dashboard', slug=client_slug)

    return render(request, 'modals/deletar_dashboard.html', {
        'dashboard': dashboard,
        'confirmation': confirmation,
        'client_slug': client_slug
    })
