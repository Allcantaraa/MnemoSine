from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from .models import Organization, OrganizationMember
from .decorators import organization_admin_required, organization_required


@login_required
def criar_organizacao(request):
    """Cria uma nova organização."""
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()

        if not name:
            messages.error(request, 'Nome da organização é obrigatório.')
            return render(request, 'organization/criar.html')

        org = Organization.objects.create(name=name, created_by=request.user)
        # Criar membershp do criador como admin
        OrganizationMember.objects.create(
            organization=org,
            user=request.user,
            role=OrganizationMember.Role.ADMIN
        )

        request.session['active_org_id'] = org.id
        messages.success(request, f'Organização "{name}" criada com sucesso!')
        return redirect('index')

    return render(request, 'organization/criar.html')


@login_required
@organization_required
def listar_membros(request):
    """Lista todos os membros da organização ativa."""
    org = request.organization
    membros = OrganizationMember.objects.filter(organization=org).select_related('user')

    return render(request, 'organization/membros.html', {
        'organization': org,
        'membros': membros
    })


@login_required
@organization_admin_required
def alterar_role_membro(request, user_id):
    """Altera o role de um membro."""
    org = request.organization

    try:
        membership = OrganizationMember.objects.get(
            organization=org,
            user_id=user_id
        )
    except OrganizationMember.DoesNotExist:
        messages.error(request, 'Membro não encontrado.')
        return redirect('listar_membros')

    if request.method == 'POST':
        new_role = request.POST.get('role', '').strip()

        if new_role not in [OrganizationMember.Role.ADMIN, OrganizationMember.Role.MEMBER, OrganizationMember.Role.VIEWER]:
            messages.error(request, 'Role inválido.')
            return redirect('listar_membros')

        membership.role = new_role
        membership.save()
        messages.success(request, f'Role do membro alterado para "{new_role}".')
        return redirect('listar_membros')

    return render(request, 'organization/alterar_role.html', {
        'membership': membership,
        'organization': org
    })


@login_required
@organization_admin_required
def remover_membro(request, user_id):
    """Remove um membro da organização."""
    org = request.organization

    try:
        membership = OrganizationMember.objects.get(
            organization=org,
            user_id=user_id
        )
    except OrganizationMember.DoesNotExist:
        messages.error(request, 'Membro não encontrado.')
        return redirect('listar_membros')

    if request.method == 'POST':
        user_name = membership.user.username
        membership.delete()
        messages.success(request, f'Membro "{user_name}" removido da organização.')
        return redirect('listar_membros')

    return render(request, 'organization/remover_membro.html', {
        'membership': membership,
        'organization': org
    })


@login_required
@organization_admin_required
def gerar_novo_codigo(request):
    """Gera um novo código de convite para a organização."""
    org = request.organization

    if request.method == 'POST':
        from .models import generate_organization_code
        org.code = generate_organization_code()
        org.save()
        messages.success(request, 'Novo código gerado com sucesso!')
        return redirect('listar_membros')

    return render(request, 'organization/gerar_codigo.html', {
        'organization': org
    })


@login_required
def entrar_organizacao(request):
    """Permite um usuário entrar em uma organização usando um código."""
    if request.method == 'POST':
        code = request.POST.get('code', '').strip().upper()

        if not code:
            messages.error(request, 'Código é obrigatório.')
            return render(request, 'organization/entrar.html')

        try:
            org = Organization.objects.get(code__iexact=code)

            # Verificar se o usuário já é membro
            if OrganizationMember.objects.filter(user=request.user, organization=org).exists():
                messages.warning(request, 'Você já é membro desta organização.')
                request.session['active_org_id'] = org.id
                return redirect('index')

            # Criar membership com role de member
            OrganizationMember.objects.create(
                organization=org,
                user=request.user,
                role=OrganizationMember.Role.MEMBER
            )

            request.session['active_org_id'] = org.id
            messages.success(request, f'Você entrou na organização "{org.name}" com sucesso!')
            return redirect('index')

        except Organization.DoesNotExist:
            messages.error(request, 'Código inválido. Verifique e tente novamente.')

    return render(request, 'organization/entrar.html')


@login_required
def selecionar_organizacao(request):
    """Permite que o usuário selecione qual organização está ativa."""
    if request.method == 'POST':
        org_id = request.POST.get('organization')

        try:
            org = Organization.objects.get(id=org_id)

            # Verificar se o usuário é membro
            if not OrganizationMember.objects.filter(user=request.user, organization=org).exists():
                messages.error(request, 'Você não é membro desta organização.')
                return redirect(reverse('perfil')) # Redirecionar para perfil se não for membro

            request.session['active_org_id'] = org.id
            messages.success(request, f'Organização "{org.name}" selecionada.')

        except Organization.DoesNotExist:
            messages.error(request, 'Organização não encontrada.')

        return redirect('index')

    # GET: mostrar lista de organizações do usuário
    org_memberships = OrganizationMember.objects.filter(user=request.user).select_related('organization')

    return render(request, 'organization/selecionar.html', {
        'memberships': org_memberships
    })
