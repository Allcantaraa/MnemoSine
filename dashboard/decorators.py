from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from .models import Organization, OrganizationMember


def get_user_active_organization(user):
    """Retorna a organização ativa do usuário da sessão ou primeira org."""
    # Implementar quando temos acesso à request
    pass


def get_user_role_in_organization(user, organization):
    """Retorna o role do usuário em uma organização."""
    try:
        membership = OrganizationMember.objects.get(user=user, organization=organization)
        return membership.role
    except OrganizationMember.DoesNotExist:
        return None


def organization_required(view_func):
    """Decorador que verifica se o usuário é membro de uma organização."""
    @wraps(view_func)
    def wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')

        # Tenta pegar a org ativa da sessão
        active_org_id = request.session.get('active_org_id')
        
        # SEMPRE passa todas as organizações do usuário para o template
        request.user_organizations = OrganizationMember.objects.filter(user=request.user).select_related('organization')

        if active_org_id:
            try:
                org = Organization.objects.get(id=active_org_id)
                if not OrganizationMember.objects.filter(user=request.user, organization=org).exists():
                    messages.error(request, 'Você não é membro desta organização.')
                    return redirect('index')
                request.organization = org
            except Organization.DoesNotExist:
                # Organização foi deletada, limpar sessão e tentar pegar outra
                if 'active_org_id' in request.session:
                    del request.session['active_org_id']
                membership = OrganizationMember.objects.filter(user=request.user).first()
                if membership:
                    request.organization = membership.organization
                    request.session['active_org_id'] = membership.organization.id
                    messages.info(request, f'Organização anterior deletada. Carregando: {membership.organization.name}')
                else:
                    messages.error(request, 'Você não pertence a nenhuma organização.')
                    return redirect('index') # Mudado de criar_organizacao para index
        else:
            # Tenta pegar a primeira org do usuário
            membership = OrganizationMember.objects.filter(user=request.user).first()
            if membership:
                request.organization = membership.organization
                request.session['active_org_id'] = membership.organization.id
            else:
                messages.error(request, 'Você não pertence a nenhuma organização.')
                return redirect('index') # Mudado de criar_organizacao para index

        return view_func(request, *args, **kwargs)
    return wrapped_view


def organization_admin_required(view_func):
    """Decorador que verifica se o usuário é administrador de uma organização."""
    @wraps(view_func)
    def wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')

        active_org_id = request.session.get('active_org_id')
        
        # SEMPRE passa todas as organizações do usuário para o template
        request.user_organizations = OrganizationMember.objects.filter(user=request.user).select_related('organization')

        if not active_org_id:
            # Tenta pegar a primeira org onde o usuário é admin
            membership = OrganizationMember.objects.filter(
                user=request.user, 
                role=OrganizationMember.Role.ADMINISTRADOR
            ).first()
            
            if membership:
                active_org_id = membership.organization.id
                request.session['active_org_id'] = active_org_id
            else:
                messages.error(request, 'Selecione uma organização ou você não tem permissão de administrador.')
                return redirect('index')

        try:
            org = Organization.objects.get(id=active_org_id)
            membership = OrganizationMember.objects.get(user=request.user, organization=org)

            if membership.role != OrganizationMember.Role.ADMINISTRADOR:
                messages.error(request, 'Você não tem permissão para acessar essa área.')
                return redirect('index')

            request.organization = org
        except Organization.DoesNotExist:
            # Organização foi deletada, limpar sessão
            if 'active_org_id' in request.session:
                del request.session['active_org_id']
            messages.error(request, 'Organização deletada. Selecione outra.')
            return redirect('index')
        except OrganizationMember.DoesNotExist:
            messages.error(request, 'Acesso negado.')
            return redirect('index')

        return view_func(request, *args, **kwargs)
    return wrapped_view


def organization_member_or_admin_required(view_func):
    """Decorador que verifica se o usuário é membro ou administrador."""
    @wraps(view_func)
    def wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')

        active_org_id = request.session.get('active_org_id')
        
        # SEMPRE passa todas as organizações do usuário para o template
        request.user_organizations = OrganizationMember.objects.filter(user=request.user).select_related('organization')

        if not active_org_id:
            messages.error(request, 'Selecione uma organização.')
            return redirect('selecionar_organizacao')

        try:
            org = Organization.objects.get(id=active_org_id)
            # Apenas verifica se o usuário é membro da organização
            if not OrganizationMember.objects.filter(user=request.user, organization=org).exists():
                messages.error(request, 'Você não tem permissão para editar.')
                return redirect('index')

            request.organization = org
        except Organization.DoesNotExist:
            # Organização foi deletada, limpar sessão
            if 'active_org_id' in request.session:
                del request.session['active_org_id']
            messages.error(request, 'Organização deletada. Selecione outra.')
            return redirect('selecionar_organizacao')
        except OrganizationMember.DoesNotExist:
            messages.error(request, 'Acesso negado.')
            return redirect('selecionar_organizacao')

        return view_func(request, *args, **kwargs)
    return wrapped_view
