from django.db import models
from django.contrib.auth.models import User
from utils.slugs import new_slugify
from django.core.exceptions import ValidationError
import secrets
import string

def generate_organization_code():
    """Gera um código único para convite de organização."""
    chars = string.ascii_letters + string.digits
    return ''.join(secrets.choice(chars) for _ in range(12))

class Organization(models.Model):
    class Meta:
        verbose_name = 'Organization'
        verbose_name_plural = 'Organizations'

    name = models.CharField(max_length=255, blank=False, null=False)
    code = models.CharField(max_length=12, unique=True, default=generate_organization_code)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owned_organizations')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class OrganizationMember(models.Model):
    class Role(models.TextChoices):
        ADMIN = 'admin', 'Admin'
        MEMBER = 'member', 'Member'
        VIEWER = 'viewer', 'Viewer'

    class Meta:
        verbose_name = 'Organization Member'
        verbose_name_plural = 'Organization Members'
        unique_together = ('organization', 'user')

    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='members')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='organization_memberships')
    role = models.CharField(max_length=10, choices=Role.choices, default=Role.MEMBER)
    joined_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.organization.name} ({self.role})"

class Cliente(models.Model):
    class Tier(models.TextChoices):
        SILVER = 'silver', 'Silver'
        GOLD = 'gold', 'Gold'
        PLATINUM = 'platinum', 'Platinum'

    class Meta:
        verbose_name = 'Cliente'
        verbose_name_plural = 'Clientes'

    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='clientes', null=False, blank=False)
    name = models.CharField(max_length=255, blank=False, null=False)
    logo = models.ImageField(upload_to='pictures/%Y/%m/', blank=True)
    description = models.TextField(max_length=100, blank=True, null=True)
    tier = models.CharField(max_length=10, choices=Tier.choices, default=Tier.SILVER)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    slug = models.SlugField(unique=True, default='', null=False, blank=True, max_length=255)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = new_slugify(self.name)
        return super().save(*args, **kwargs)

class Categoria(models.Model):
    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'

    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='categorias')
    name = models.CharField(max_length=255, blank=False, null=False)
    slug = models.SlugField(
        unique=True,
        default=None,
        null=True,
        blank=True,
        max_length=255
    )

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = new_slugify(self.name)
        return super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class Dashboard(models.Model):
    class PublicoAlvo(models.TextChoices):
        GESTORES = 'ges', 'Gestores'
        TECNICOS = 'tec', 'Tecnicos'
        OUTROS = 'out', 'Outros'

    class AnaliticoOuMacro(models.TextChoices):
        ANALITICO = 'an', 'Analitico'
        Macro = 'ma', 'Macro'

    class Meta:
        verbose_name = 'Dashboard'
        verbose_name_plural = 'Dashboards'

    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='dashboards')
    client = models.ForeignKey(Cliente, on_delete=models.SET_NULL, null=True)
    title = models.CharField(max_length=255, blank=False, null=False)
    categories = models.ManyToManyField(Categoria, related_name='dashboards', blank=True)
    purpose = models.CharField(max_length=255, blank=True, null=True)
    target_audience = models.CharField(max_length=3, choices=PublicoAlvo.choices, default=PublicoAlvo.OUTROS)
    kpis_displayed = models.CharField(max_length=255, blank=True, null=True)
    analytical_or_macro = models.CharField(max_length=2, choices=AnaliticoOuMacro.choices, default=AnaliticoOuMacro.Macro)
    data_source = models.CharField(max_length=111, blank=False, null=False)
    panel_preference = models.CharField(max_length=255, blank=True, null=True)
    color_preference = models.CharField(max_length=60, blank=True, null=True)
    screen_resolution = models.CharField(max_length=60, blank=True, null=True)
    image = models.ImageField(upload_to='dashboards/images/%Y/%m/', blank=False, null=False)
    json = models.FileField(upload_to='dashboards/json/%Y/%m/', blank=False, null=False)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='dashboards_created')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    slug = models.SlugField(
        unique=True,
        default=None,
        null=True,
        blank=True,
        max_length=255
    )

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = new_slugify(self.title)
        return super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.client.name} - {self.title}" if self.client else self.title