from django import template
from dashboard.models import OrganizationMember

register = template.Library()


@register.filter
def has_org_role(user, org):
    """Verifica se o usuário é administrador da organização."""
    if not user or not org or not user.is_authenticated:
        return False
        
    try:
        # Extrair ID se for um objeto Lazy
        org_id = org.id if hasattr(org, 'id') else org
        if not org_id:
            return False
            
        membership = OrganizationMember.objects.filter(user=user, organization_id=org_id).first()
        return membership and membership.role == OrganizationMember.Role.ADMINISTRADOR
    except Exception:
        return False


@register.filter
def get_org_role(user, org):
    """Retorna o role do usuário em uma organização."""
    try:
        membership = OrganizationMember.objects.get(user=user, organization=org)
        return membership.get_role_display()
    except OrganizationMember.DoesNotExist:
        return 'N/A'
