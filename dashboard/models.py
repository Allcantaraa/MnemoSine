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

    PRINCIPAL = 'Principal'
    MODELOS = 'Modelos'
    ALLOWED_NAMES = [PRINCIPAL, MODELOS]

    name = models.CharField(max_length=255, blank=False, null=False, unique=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owned_organizations')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if self.name not in self.ALLOWED_NAMES:
            raise ValidationError(f"Apenas as organizações '{self.PRINCIPAL}' e '{self.MODELOS}' são permitidas.")
        
        # Bloquear criação se já existirem as duas (se for um novo objeto)
        if not self.pk:
            if Organization.objects.filter(name=self.name).exists():
                raise ValidationError(f"A organização '{self.name}' já existe.")
        
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise ValidationError("Não é permitido excluir organizações no sistema.")

class OrganizationMember(models.Model):
    class Role(models.TextChoices):
        ADMINISTRADOR = 'administrador', 'Administrador'
        MEMBRO = 'membro', 'Membro'

    class Meta:
        verbose_name = 'Organization Member'
        verbose_name_plural = 'Organization Members'
        unique_together = ('organization', 'user')

    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='members')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='organization_memberships')
    role = models.CharField(max_length=15, choices=Role.choices, default=Role.MEMBRO)
    joined_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.organization.name} ({self.get_role_display()})"

class DeletionRequest(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pending', 'Pendente'
        APPROVED = 'approved', 'Aprovado'
        REJECTED = 'rejected', 'Rejeitado'

    class ContentType(models.TextChoices):
        CLIENTE = 'cliente', 'Cliente'
        DASHBOARD = 'dashboard', 'Dashboard'
        CATEGORIA = 'categoria', 'Categoria'

    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='deletion_requests')
    requested_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='deletion_requests_made')
    content_type = models.CharField(max_length=20, choices=ContentType.choices)
    object_id = models.PositiveIntegerField()
    object_name = models.CharField(max_length=255)
    reason = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='deletion_requests_reviewed')
    review_notes = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Solicitação de Exclusão'
        verbose_name_plural = 'Solicitações de Exclusão'

    def __str__(self):
        return f"Solicitação de exclusão: {self.get_content_type_display()} - {self.object_name} ({self.get_status_display()})"

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
        if self.pk:
            original = type(self).objects.filter(pk=self.pk).only('name', 'slug').first()
            if original and original.name != self.name:
                self.slug = new_slugify(self.name)
        elif not self.slug:
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
    class Meta:
        verbose_name = 'Dashboard'
        verbose_name_plural = 'Dashboards'

    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='dashboards')
    client = models.ForeignKey(Cliente, on_delete=models.SET_NULL, null=True)
    title = models.CharField(max_length=255, blank=False, null=False)
    categories = models.ManyToManyField(Categoria, related_name='dashboards', blank=True)
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