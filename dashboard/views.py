from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.db.models import Count, Q
from django.http import JsonResponse
from django.http import FileResponse
import os
from dashboard.models import Cliente, Dashboard, Categoria, OrganizationMember, DeletionRequest
from dashboard.forms import ClienteForm, CategoriaForm, DashboardForm
from dashboard.decorators import organization_required, organization_member_or_admin_required, organization_admin_required

@login_required
@organization_member_or_admin_required
def toggle_favorite_cliente(request, slug):
    """Adiciona ou remove um cliente dos favoritos do usuário via Fetch API."""
    if request.method == 'POST':
        org = request.organization
        cliente = get_object_or_404(Cliente, slug=slug, organization=org)
        
        if request.user in cliente.favorited_by.all():
            cliente.favorited_by.remove(request.user)
            is_favorite = False
        else:
            cliente.favorited_by.add(request.user)
            is_favorite = True
            
        return JsonResponse({'success': True, 'is_favorite': is_favorite})
        
    return JsonResponse({'success': False, 'error': 'Método não permitido'}, status=405)

@login_required
@organization_member_or_admin_required
def api_recomendacoes_dashboards(request):
    """API que retorna recomendações baseadas no termo de busca em toda a organização."""
    org = request.organization
    termo = request.GET.get('q', '').strip()

    if not termo:
        return JsonResponse({'dashboards': []})

    # Busca em toda a organização por título que contenha o termo
    recomendacoes = Dashboard.objects.filter(
        organization=org,
        title__icontains=termo
    ).select_related('client')[:6] # Limita a 6 para não poluir a tela

    resultados = []
    for dash in recomendacoes:
        resultados.append({
            'id': dash.id,
            'title': dash.title,
            'client_name': dash.client.name if dash.client else 'Geral',
            'client_slug': dash.client.slug if dash.client else '',
            'image_url': dash.image.url if dash.image else '',
            'download_url': reverse('baixar_dashboard_json', args=[dash.client.slug, dash.slug]) if dash.client else '#'
        })

    return JsonResponse({'dashboards': resultados})

@login_required
@organization_required
def index(request):
    """Página principal com KPIs, clientes e filtros."""
    org = request.organization

    search_query = request.GET.get('search', '').strip()
    category_filter = request.GET.get('category', '')

    total_clientes = Cliente.objects.filter(organization=org).count()
    total_dashboards = Dashboard.objects.filter(organization=org).count()
    membros_count = OrganizationMember.objects.filter(organization=org).count()

    # Anotamos os favoritos
    clientes_qs = Cliente.objects.filter(organization=org).annotate(
        is_favorite=Count('favorited_by', filter=Q(favorited_by=request.user))
    ).order_by('-is_favorite', '-created_at')

    # Separamos em duas listas para o template
    clientes_favoritos = [c for c in clientes_qs if c.is_favorite]
    clientes_normais = [c for c in clientes_qs if not c.is_favorite]

    categorias = Categoria.objects.filter(organization=org)
    dashboards_qs = Dashboard.objects.filter(organization=org)

    if category_filter:
        try:
            category = Categoria.objects.get(id=category_filter, organization=org)
            dashboards_qs = dashboards_qs.filter(categories=category)
        except Categoria.DoesNotExist:
            pass

    if search_query:
        dashboards_qs = dashboards_qs.filter(title__icontains=search_query)

    dashboards_qs = dashboards_qs.distinct()

    return render(request, 'index.html', {
        'clientes_favoritos': clientes_favoritos, # Nova variável
        'clientes_normais': clientes_normais,     # Nova variável
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
    
    category_filter = request.GET.get('category', '')
    
    dashboards_qs = Dashboard.objects.filter(client=cliente)
    
    if category_filter:
        try:
            category = Categoria.objects.get(id=category_filter, organization=org)
            dashboards_qs = dashboards_qs.filter(categories=category)
        except Categoria.DoesNotExist:
            pass

    # Mantemos o distinct para evitar duplicatas por causa do filtro de categorias
    dashboards_qs = dashboards_qs.distinct()
    
    # NOVIDADE: Anotamos se o usuário atual favoritou (retorna 1 ou 0) e ordenamos por isso primeiro
    dashboards_qs = dashboards_qs.annotate(
        is_favorite=Count('favorited_by', filter=Q(favorited_by=request.user))
    ).order_by('-is_favorite', '-created_at') # Favoritos primeiro, depois os mais recentes
    
    categorias = Categoria.objects.filter(organization=org)
    all_clients = Cliente.objects.filter(organization=org).order_by('name')

    return render(request, 'cliente_dashboards.html', {
        'dashboards': dashboards_qs,
        'client_slug': slug,
        'categorias': categorias,
        'cliente': cliente,
        'all_clients': all_clients,
        'selected_category': category_filter,
        'organization': org
    })


@login_required
@organization_member_or_admin_required
def toggle_favorite_dashboard(request, client_slug, dashboard_slug):
    """Adiciona ou remove um dashboard dos favoritos do usuário via Fetch API."""
    if request.method == 'POST':
        org = request.organization
        dashboard = get_object_or_404(Dashboard, slug=dashboard_slug, organization=org, client__slug=client_slug)
        
        if request.user in dashboard.favorited_by.all():
            dashboard.favorited_by.remove(request.user)
            is_favorite = False
        else:
            dashboard.favorited_by.add(request.user)
            is_favorite = True
            
        return JsonResponse({'success': True, 'is_favorite': is_favorite})
        
    return JsonResponse({'success': False, 'error': 'Método não permitido'}, status=405)

@login_required
@organization_member_or_admin_required
def favoritar_dashboards_bulk(request, client_slug):
    """Adiciona vários dashboards aos favoritos do usuário em massa."""
    org = request.organization
    cliente = get_object_or_404(Cliente, slug=client_slug, organization=org)

    if request.method == 'POST':
        dashboard_ids = request.POST.get('dashboard_ids', '').split(',')
        dashboard_ids = [id for id in dashboard_ids if id and id.isdigit()]

        if not dashboard_ids:
            messages.error(request, 'Nenhum dashboard selecionado.')
            return redirect('cliente_dashboard', slug=client_slug)

        dashboards = Dashboard.objects.filter(
            id__in=dashboard_ids, 
            organization=org, 
            client=cliente
        )

        if not dashboards.exists():
            messages.error(request, 'Nenhum dashboard encontrado.')
            return redirect('cliente_dashboard', slug=client_slug)

        count = 0
        for dashboard in dashboards:
            # O .add() do Django já é inteligente e não duplica se o usuário já estiver favoritado
            dashboard.favorited_by.add(request.user)
            count += 1

        message = f'{count} dashboard adicionado' if count == 1 else f'{count} dashboards adicionados'
        messages.success(request, f'{message} aos favoritos com sucesso!')

    return redirect('cliente_dashboard', slug=client_slug)

@login_required
@organization_required
def dashboard(request, slug):
    """Visualiza detalhes de um dashboard."""
    org = request.organization
    dashboard_obj = get_object_or_404(Dashboard, slug=slug, organization=org)
    cliente_slug = dashboard_obj.client.slug if dashboard_obj.client else None

    return render(request, 'detalhes_dashboard.html', {
        'dashboard': dashboard_obj,
        'client_slug': cliente_slug,
        'organization': org
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

        return render(request, 'cliente_criar.html', {'form': form, 'form_action': form_action, 'organization': org})

    return render(request, 'cliente_criar.html', {'form': ClienteForm(), 'form_action': form_action, 'organization': org})


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

        return render(request, 'cliente_criar.html', {'form': form, 'form_action': form_action, 'organization': org})

    return render(request, 'cliente_criar.html', {'form': ClienteForm(instance=cliente), 'form_action': form_action, 'organization': org})


@login_required
@organization_member_or_admin_required
def deletar_cliente(request, slug):
    """Deleta um cliente (admin) ou solicita exclusão (membro)."""
    org = request.organization
    cliente = get_object_or_404(Cliente, slug=slug, organization=org)
    membership = OrganizationMember.objects.get(user=request.user, organization=org)

    if request.method == 'POST':
        if membership.role == OrganizationMember.Role.ADMINISTRADOR:
            cliente.delete()
            messages.success(request, f'Cliente "{cliente.name}" removido com sucesso.')
        else:
            # Criar solicitação de exclusão
            DeletionRequest.objects.create(
                organization=org,
                requested_by=request.user,
                content_type=DeletionRequest.ContentType.CLIENTE,
                object_id=cliente.id,
                object_name=cliente.name,
                reason=request.POST.get('reason', '')
            )
            messages.info(request, f'Solicitação de exclusão para o cliente "{cliente.name}" enviada aos administradores.')
        return redirect('index')

    return redirect('index')


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
def atualizar_categoria(request, client_slug, categoria_slug):
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
@organization_member_or_admin_required
def deletar_categoria(request, client_slug, categoria_slug):
    """Deleta uma categoria (admin) ou solicita exclusão (membro)."""
    org = request.organization
    categoria = get_object_or_404(Categoria, slug=categoria_slug, organization=org)
    membership = OrganizationMember.objects.get(user=request.user, organization=org)

    if request.method == 'POST':
        if membership.role == OrganizationMember.Role.ADMINISTRADOR:
            categoria.delete()
            messages.success(request, f'Categoria "{categoria.name}" removida com sucesso.')
        else:
            # Criar solicitação de exclusão
            DeletionRequest.objects.create(
                organization=org,
                requested_by=request.user,
                content_type=DeletionRequest.ContentType.CATEGORIA,
                object_id=categoria.id,
                object_name=categoria.name,
                reason=request.POST.get('reason', '')
            )
            messages.info(request, f'Solicitação de exclusão para a categoria "{categoria.name}" enviada aos administradores.')
        return redirect('cliente_dashboard', slug=client_slug)

    return redirect('cliente_dashboard', slug=client_slug)


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
            dashboard.created_by = request.user
            dashboard.save()
            form.save_m2m()
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
            dashboard = form.save(commit=False)
            dashboard.save()
            form.save_m2m()
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
@organization_member_or_admin_required
def deletar_dashboard(request, client_slug, dashboard_slug):
    """Deleta um dashboard (admin) ou solicita exclusão (membro)."""
    org = request.organization
    dashboard = get_object_or_404(Dashboard, slug=dashboard_slug, organization=org, client__slug=client_slug)
    membership = OrganizationMember.objects.get(user=request.user, organization=org)

    if request.method == 'POST':
        if membership.role == OrganizationMember.Role.ADMINISTRADOR:
            dashboard.delete()
            messages.success(request, f'Dashboard "{dashboard.title}" removido com sucesso.')
        else:
            # Criar solicitação de exclusão
            DeletionRequest.objects.create(
                organization=org,
                requested_by=request.user,
                content_type=DeletionRequest.ContentType.DASHBOARD,
                object_id=dashboard.id,
                object_name=dashboard.title,
                reason=request.POST.get('reason', '')
            )
            messages.info(request, f'Solicitação de exclusão para o dashboard "{dashboard.title}" enviada aos administradores.')
        return redirect('cliente_dashboard', slug=client_slug)

    return redirect('cliente_dashboard', slug=client_slug)


@login_required
@organization_required
def baixar_dashboard_json(request, client_slug, dashboard_slug):
    """Faz download do arquivo JSON do dashboard."""
    org = request.organization
    dashboard = get_object_or_404(Dashboard, slug=dashboard_slug, organization=org, client__slug=client_slug)
    
    # Verificar permissão (qualquer membro pode ver)
    if not dashboard.json:
        messages.error(request, 'Arquivo JSON não encontrado.')
        return redirect('cliente_dashboard', slug=client_slug)
    
    # Obter o caminho do arquivo
    file_path = dashboard.json.path
    
    if os.path.exists(file_path):
        response = FileResponse(open(file_path, 'rb'), content_type='application/json')
        response['Content-Disposition'] = f'attachment; filename="{dashboard.title}-{dashboard.slug}.json"'
        return response
    else:
        messages.error(request, 'Arquivo JSON não encontrado no servidor.')
        return redirect('cliente_dashboard', slug=client_slug)


@login_required
@organization_member_or_admin_required
def mover_dashboards(request, client_slug):
    """Move muitos dashboards para outro cliente."""
    org = request.organization
    cliente_atual = get_object_or_404(Cliente, slug=client_slug, organization=org)

    if request.method == 'POST':
        dashboard_ids = request.POST.get('dashboard_ids', '').split(',')
        destination_client_id = request.POST.get('destination_client')

        # Validar que recebemos os dados
        if not dashboard_ids or not dashboard_ids[0] or not destination_client_id:
            messages.error(request, 'Selecione um cliente de destino.')
            return redirect('cliente_dashboard', slug=client_slug)

        # Obter cliente de destino
        try:
            destination_client = Cliente.objects.get(id=destination_client_id, organization=org)
        except Cliente.DoesNotExist:
            messages.error(request, 'Cliente de destino inválido.')
            return redirect('cliente_dashboard', slug=client_slug)

        # Garantir que não é o mesmo cliente
        if destination_client.id == cliente_atual.id:
            messages.error(request, 'Selecione um cliente diferente do atual.')
            return redirect('cliente_dashboard', slug=client_slug)

        # Filtrar IDs válidos (apenas números)
        dashboard_ids = [id for id in dashboard_ids if id and id.isdigit()]

        if not dashboard_ids:
            messages.error(request, 'Nenhum dashboard selecionado.')
            return redirect('cliente_dashboard', slug=client_slug)

        # Buscar dashboards
        dashboards = Dashboard.objects.filter(
            id__in=dashboard_ids,
            organization=org,
            client=cliente_atual
        )

        if not dashboards.exists():
            messages.error(request, 'Nenhum dashboard encontrado para mover.')
            return redirect('cliente_dashboard', slug=client_slug)

        # Mover dashboards
        count = dashboards.count()
        dashboards.update(client=destination_client)

        message = f'{count} dashboard foi movido' if count == 1 else f'{count} dashboards foram movidos'
        messages.success(request, f'{message} para {destination_client.name} com sucesso!')
        return redirect('cliente_dashboard', slug=client_slug)

    return redirect('cliente_dashboard', slug=client_slug)


@login_required
@organization_member_or_admin_required
def deletar_dashboards_bulk(request, client_slug):
    """Deleta vários dashboards (admin) ou solicita exclusão (membro)."""
    org = request.organization
    cliente = get_object_or_404(Cliente, slug=client_slug, organization=org)
    membership = OrganizationMember.objects.get(user=request.user, organization=org)

    if request.method == 'POST':
        dashboard_ids = request.POST.get('dashboard_ids', '').split(',')
        dashboard_ids = [id for id in dashboard_ids if id and id.isdigit()]

        if not dashboard_ids:
            messages.error(request, 'Nenhum dashboard selecionado.')
            return redirect('cliente_dashboard', slug=client_slug)

        dashboards = Dashboard.objects.filter(
            id__in=dashboard_ids,
            organization=org,
            client=cliente
        )

        if not dashboards.exists():
            messages.error(request, 'Nenhum dashboard encontrado.')
            return redirect('cliente_dashboard', slug=client_slug)

        if membership.role == OrganizationMember.Role.ADMINISTRADOR:
            count = dashboards.count()
            dashboards.delete()
            message = f'{count} dashboard foi deletado' if count == 1 else f'{count} dashboards foram deletados'
            messages.success(request, f'{message} com sucesso!')
        else:
            # Para bulk, criamos uma solicitação para cada um ou uma consolidada?
            # Vamos criar uma para cada para simplificar a aprovação individual
            for db in dashboards:
                DeletionRequest.objects.create(
                    organization=org,
                    requested_by=request.user,
                    content_type=DeletionRequest.ContentType.DASHBOARD,
                    object_id=db.id,
                    object_name=db.title,
                    reason=request.POST.get('reason', 'Exclusão em massa')
                )
            messages.info(request, f'{dashboards.count()} solicitações de exclusão enviadas aos administradores.')

        return redirect('cliente_dashboard', slug=client_slug)

    return redirect('cliente_dashboard', slug=client_slug)

@login_required
@organization_member_or_admin_required
def duplicar_dashboards_bulk(request, client_slug):
    """Duplica vários dashboards selecionados."""
    org = request.organization
    cliente = get_object_or_404(Cliente, slug=client_slug, organization=org)

    if request.method == 'POST':
        dashboard_ids = request.POST.get('dashboard_ids', '').split(',')
        dashboard_ids = [id for id in dashboard_ids if id and id.isdigit()]

        if not dashboard_ids:
            messages.error(request, 'Nenhum dashboard selecionado para duplicar.')
            return redirect('cliente_dashboard', slug=client_slug)

        dashboards = Dashboard.objects.filter(
            id__in=dashboard_ids, 
            organization=org, 
            client=cliente
        )

        if not dashboards.exists():
            messages.error(request, 'Nenhum dashboard encontrado.')
            return redirect('cliente_dashboard', slug=client_slug)

        count = 0
        for dashboard in dashboards:
            # 1. Salvar as categorias atuais na memória antes de duplicar
            categorias_antigas = list(dashboard.categories.all())

            # 2. Remover IDs e atualizar o título para criar um novo registro
            dashboard.pk = None
            dashboard.id = None
            dashboard.title = f"{dashboard.title} (Cópia)"
            dashboard.slug = None  # Limpar o slug para que o model gere um novo automaticamente
            
            # 3. Salvar o novo dashboard
            dashboard.save()

            # 4. Vincular as categorias antigas à nova cópia
            dashboard.categories.set(categorias_antigas)
            count += 1

        message = f'{count} dashboard foi duplicado' if count == 1 else f'{count} dashboards foram duplicados'
        messages.success(request, f'{message} com sucesso!')

    return redirect('cliente_dashboard', slug=client_slug)


@login_required
@organization_admin_required
def listar_notificacoes(request):
    """Lista solicitações de exclusão pendentes (apenas admin)."""
    org = request.organization
    solicitacoes = DeletionRequest.objects.filter(
        organization=org,
        status=DeletionRequest.Status.PENDING
    ).select_related('requested_by')

    historico = DeletionRequest.objects.filter(
        organization=org
    ).exclude(status=DeletionRequest.Status.PENDING).select_related('requested_by', 'reviewed_by')[:20]

    return render(request, 'notificacoes.html', {
        'solicitacoes': solicitacoes,
        'historico': historico,
        'organization': org
    })


@login_required
@organization_admin_required
def revisar_solicitacao(request, request_id):
    """Aprova ou rejeita uma solicitação de exclusão."""
    org = request.organization
    solicitacao = get_object_or_404(DeletionRequest, id=request_id, organization=org)

    if request.method == 'POST':
        acao = request.POST.get('action')
        notas = request.POST.get('notes', '')

        if acao == 'approve':
            # Tentar deletar o objeto
            deleted = False
            try:
                if solicitacao.content_type == DeletionRequest.ContentType.CLIENTE:
                    obj = Cliente.objects.get(id=solicitacao.object_id, organization=org)
                    obj.delete()
                    deleted = True
                elif solicitacao.content_type == DeletionRequest.ContentType.CATEGORIA:
                    obj = Categoria.objects.get(id=solicitacao.object_id, organization=org)
                    obj.delete()
                    deleted = True
                elif solicitacao.content_type == DeletionRequest.ContentType.DASHBOARD:
                    obj = Dashboard.objects.get(id=solicitacao.object_id, organization=org)
                    obj.delete()
                    deleted = True
            except (Cliente.DoesNotExist, Categoria.DoesNotExist, Dashboard.DoesNotExist):
                messages.warning(request, 'O item já foi removido ou não existe mais.')
                solicitacao.status = DeletionRequest.Status.APPROVED # Marcar como aprovado mesmo assim se sumiu
            
            if deleted:
                solicitacao.status = DeletionRequest.Status.APPROVED
                messages.success(request, f'Solicitação aprovada e item "{solicitacao.object_name}" removido.')
            
        elif acao == 'reject':
            solicitacao.status = DeletionRequest.Status.REJECTED
            messages.info(request, f'Solicitação para "{solicitacao.object_name}" rejeitada.')

        solicitacao.reviewed_by = request.user
        solicitacao.review_notes = notas
        solicitacao.save()

    return redirect('listar_notificacoes')
