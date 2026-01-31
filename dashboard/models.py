from django.db import models
from django.contrib.auth.models import User
from utils.slugs import new_slugify
from django.core.exceptions import ValidationError

class Cliente(models.Model) :
    class Meta :
        verbose_name = 'Cliente'
        verbose_name_plural = 'Clientes'
    
    owner = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    name = models.CharField(max_length=255,blank=False, null=False)
    logo = models.ImageField(upload_to='pictures/%Y/%m/', blank=True)
    description = models.TextField(max_length=100,blank=True, null=True)
    is_vip = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    slug = models.SlugField(unique=True, default='', null=False, blank=True, max_length=255)
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs) :
        if not self.slug :
            self.slug = new_slugify(self.name)
        return super().save(*args, **kwargs)
    

class Categoria(models.Model) :
    class Meta :
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'
    
    owner = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    name = models.CharField(max_length=255, blank=False, null=False)
    slug = models.SlugField(
        unique=True,
        default=None,
        null=True,
        blank=True,
        max_length=255
    )
    
    def save(self, *args, **kwargs) :
        if not self.slug :
            self.slug = new_slugify(self.name)
        return super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name

class Dashboard(models.Model) :
    
    class Status(models.TextChoices) :
        NOVO = 'nv', 'Novo'
        EM_EXECUCAO = 'ex', 'Em Execução'
        CONCLUIDO = 'cn', 'Concluido'
        
    class PublicoAlvo(models.TextChoices) :
        GESTORES = 'ges', 'Gestores'
        TECNICOS = 'tec', 'Tecnicos'
        OUTROS = 'out', 'Outros'
        
    class AnaliticoOuMacro(models.TextChoices) :
        ANALITICO = 'an', 'Analitico'
        Macro = 'ma', 'Macro'
    
    class Meta :
        verbose_name = 'Dashboard'
        verbose_name_plural = 'Dashboards'
    
    owner = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    client = models.ForeignKey(Cliente, on_delete=models.SET_NULL, null=True)
    title = models.CharField(max_length=255, blank=False, null=False)
    category = models.ForeignKey(Categoria, on_delete=models.SET_NULL, null=True)
    status = models.CharField(max_length=2, choices=Status.choices, default=Status.NOVO)
    purpose = models.CharField(max_length=255, blank=True, null= True)
    target_audience = models.CharField(max_length=3, choices=PublicoAlvo.choices, default=PublicoAlvo.OUTROS)
    kpis_displayed = models.CharField(max_length=255, blank=True, null=True)
    analytical_or_macro = models.CharField(max_length=2, choices=AnaliticoOuMacro.choices, default=AnaliticoOuMacro.Macro)
    data_source = models.CharField(max_length=111, blank=False, null=False)
    panel_preference = models.CharField(max_length=255, blank=True, null=True)
    color_preference = models.CharField(max_length=60, blank=True, null=True)
    screen_resolution = models.CharField(max_length=60, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    json = models.FileField(upload_to='dashboards/json/%Y/%m/',blank=True, null=True)
    slug = models.SlugField(
        unique=True,
        default=None,
        null=True,
        blank=True,
        max_length=255
    )
    
    def clean(self) :
        if self.status == 'cn' :
                if not self.json :
                    raise ValidationError('O arquivo JSON é obrigatório para conclusão.')
                
                if not str(self.json).endswith('.json') :
                    raise ValidationError('É necessário que o arquivo seja um JSON')
    
    def save(self, *args, **kwargs) :
        if not self.slug :
            self.slug = new_slugify(self.title)
        return super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.client.name} - {self.title}"
    
class DashboardImage(models.Model) :
    dashboard = models.ForeignKey(Dashboard, on_delete=models.CASCADE, related_name='dashboard_images')
    images = models.ImageField(upload_to='dashboards/images/%Y/%m/', blank=True, null=True) 
    description = models.TextField(max_length=100,blank=True, null=True)