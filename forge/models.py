from django.db import models
from django.contrib.auth.models import User
from dashboard.models import Organization
from utils.slugs import new_slugify


class Category(models.Model):
    class Meta:
        verbose_name = 'Categoria'
        verbose_name_plural = 'Categorias'
        ordering = ['name']
        unique_together = ('organization', 'name')

    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='forge_categories')
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class CodeEntry(models.Model):
    class Type(models.TextChoices):
        HTML_GRAPHICS = 'html_graphics', 'HTML Graphics'
        HTML_TEXT = 'html_text', 'HTML / Text Panel'
        BUSINESS_TEXT = 'business_text', 'Business Text'
        BUSINESS_CHARTS = 'business_charts', 'Business Charts'
        CANVAS = 'canvas', 'Canvas'
        DASHBOARD_JSON = 'dashboard_json', 'Dashboard JSON'
        SQL = 'sql', 'SQL Query'
        JAVASCRIPT = 'javascript', 'JavaScript'
        CSS = 'css', 'CSS'
        SVG = 'svg', 'SVG'

    class Status(models.TextChoices):
        DRAFT = 'draft', 'Draft'
        ACTIVE = 'active', 'Ativo'

    class Meta:
        verbose_name = 'Código'
        verbose_name_plural = 'Códigos'
        ordering = ['-created_at']

    organization = models.ForeignKey(
        Organization, on_delete=models.CASCADE, related_name='forge_codes'
    )
    favorited_by = models.ManyToManyField(User, related_name='favorite_forge_codes', blank=True)
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, max_length=255, blank=True)
    type = models.CharField(max_length=50, choices=Type.choices)
    category = models.CharField(max_length=100, blank=True, default='')
    description = models.TextField(blank=True, default='')
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)
    content = models.JSONField()
    thumbnail = models.ImageField(upload_to='forge/thumbnails/%Y/%m/', blank=True, null=True)
    version = models.CharField(max_length=50, default='1.0.0')
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name='forge_codes_created'
    )
    view_count = models.PositiveIntegerField(default=0)
    copy_count = models.PositiveIntegerField(default=0)
    export_count = models.PositiveIntegerField(default=0)
    edit_count = models.PositiveIntegerField(default=0)
    last_used_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if self.pk:
            original = type(self).objects.filter(pk=self.pk).only('name', 'slug').first()
            if original and original.name != self.name:
                self.slug = new_slugify(self.name)
        elif not self.slug:
            self.slug = new_slugify(self.name)
        super().save(*args, **kwargs)

    @property
    def score(self):
        return self.view_count + (self.copy_count * 2) + (self.export_count * 2) + self.edit_count

    @property
    def is_previewable(self):
        return self.type in (
            self.Type.HTML_GRAPHICS, self.Type.HTML_TEXT, self.Type.BUSINESS_TEXT
        )

    @property
    def content_json_str(self):
        import json
        return json.dumps(self.content)


class AgentLog(models.Model):
    class Meta:
        verbose_name = 'Log do Agente'
        verbose_name_plural = 'Logs do Agente'
        ordering = ['-created_at']

    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='agent_logs')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='agent_logs')
    prompt = models.TextField()
    reply = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user} — {self.created_at:%Y-%m-%d %H:%M}'


class CodeVersion(models.Model):
    class Meta:
        verbose_name = 'Versão'
        verbose_name_plural = 'Versões'
        ordering = ['-created_at']

    code = models.ForeignKey(CodeEntry, on_delete=models.CASCADE, related_name='versions')
    version = models.CharField(max_length=50)
    content = models.JSONField()
    changelog = models.TextField(blank=True, default='')
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.code.name} — v{self.version}'
