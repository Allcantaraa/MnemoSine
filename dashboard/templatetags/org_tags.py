from django import template
from dashboard.models import OrganizationMember

register = template.Library()


@register.filter
def has_org_role(user, org):
    """Verifica se o usuário é admin da organização."""
    try:
        membership = OrganizationMember.objects.get(user=user, organization=org)
        return membership.role == OrganizationMember.Role.ADMIN
    except OrganizationMember.DoesNotExist:
        return False


@register.filter
def get_org_role(user, org):
    """Retorna o role do usuário em uma organização."""
    try:
        membership = OrganizationMember.objects.get(user=user, organization=org)
        return membership.get_role_display()
    except OrganizationMember.DoesNotExist:
        return 'N/A'
