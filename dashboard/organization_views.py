from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.urls import reverse
from .models import Organization, OrganizationMember
from .decorators import organization_admin_required, organization_required
from .forms import OrganizationUserCreateForm


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

        if new_role not in [OrganizationMember.Role.ADMINISTRADOR, OrganizationMember.Role.MEMBRO]:
            messages.error(request, 'Role inválido.')
            return redirect('listar_membros')

        # Se a organização for uma das permitidas (Principal/Modelos), atualizar em ambas
        if org.name in [Organization.PRINCIPAL, Organization.MODELOS]:
            allowed_orgs = Organization.objects.filter(name__in=[Organization.PRINCIPAL, Organization.MODELOS])
            OrganizationMember.objects.filter(
                user_id=user_id, 
                organization__in=allowed_orgs
            ).update(role=new_role)
            messages.success(request, f'Role do membro alterado para "{new_role}" nas organizações permitidas.')
        else:
            membership.role = new_role
            membership.save()
            messages.success(request, f'Role do membro alterado para "{membership.get_role_display()}".')
            
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
        
        # Se a organização for uma das permitidas, remover de ambas
        if org.name in [Organization.PRINCIPAL, Organization.MODELOS]:
            allowed_orgs = Organization.objects.filter(name__in=[Organization.PRINCIPAL, Organization.MODELOS])
            OrganizationMember.objects.filter(
                user_id=user_id, 
                organization__in=allowed_orgs
            ).delete()
            messages.success(request, f'Membro "{user_name}" removido das organizações permitidas.')
        else:
            membership.delete()
            messages.success(request, f'Membro "{user_name}" removido da organização.')
            
        return redirect('listar_membros')

    return render(request, 'organization/remover_membro.html', {
        'membership': membership,
        'organization': org
    })


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
                return redirect('perfil')

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


@login_required
@organization_admin_required
def criar_usuario_organizacao(request):
    """Cria um novo usuário e já adiciona na organização ativa."""
    org = request.organization

    if request.method != 'POST':
        return redirect('listar_membros')

    form = OrganizationUserCreateForm(request.POST)
    if form.is_valid():
        user = User.objects.create_user(
            username=form.cleaned_data['username'],
            email=form.cleaned_data['email'],
            password=form.cleaned_data['password1'],
        )
        
        # Vincular o usuário a AMBAS as organizações permitidas (Principal e Modelos)
        allowed_orgs = Organization.objects.filter(name__in=[Organization.PRINCIPAL, Organization.MODELOS])
        
        for organization in allowed_orgs:
            OrganizationMember.objects.get_or_create(
                organization=organization,
                user=user,
                defaults={'role': form.cleaned_data['role']}
            )
            
        messages.success(request, f'Usuário "{user.username}" criado e vinculado às organizações permitidas com sucesso.')
        return redirect('listar_membros')

    for field_errors in form.errors.values():
        for error in field_errors:
            messages.error(request, error)
    return redirect('listar_membros')
